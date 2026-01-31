#!/bin/bash

################################################################################
#                      SEAA Management Script
#
# Comprehensive management script for SEAA system operations:
# - Start/stop the system
# - Check status and health
# - View logs and events
# - Manage processes and ports
# - Development utilities
#
# Usage: ./manage.sh [COMMAND] [OPTIONS]
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_CMD=${PYTHON_CMD:-python3}
MAIN_PORT=${SEAA_PORT:-8000}
OLLAMA_PORT=${OLLAMA_PORT:-11434}
PID_FILE=".seaa.pid"
LOG_FILE="seaa.log"
VENV_DIR="venv"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found in $VENV_DIR"
        print_info "Run './install.sh' to set up the environment"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    fi
}

# Check if service is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi

    # Fallback: check if process is running
    if pgrep -f "python3 main.py" > /dev/null 2>&1; then
        return 0
    fi

    return 1
}

# Get PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        pgrep -f "python3 main.py" || echo ""
    fi
}

################################################################################
# Commands: Core Operations
################################################################################

cmd_start() {
    print_header "Starting SEAA System"

    if is_running; then
        print_warning "System is already running (PID: $(get_pid))"
        echo "Use './manage.sh stop' to stop it first, or './manage.sh restart'"
        exit 1
    fi

    check_venv
    activate_venv

    print_info "Starting SEAA..."

    # Start in background and save PID
    $PYTHON_CMD main.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    print_success "System started (PID: $pid)"
    print_info "Waiting for initialization..."
    sleep 3

    # Check if still running
    if is_running; then
        print_success "System is running"
        print_info "API available at: http://localhost:$MAIN_PORT"
        print_info "View logs: tail -f $LOG_FILE"
        print_info "Stop system: ./manage.sh stop"
    else
        print_error "System failed to start. Check logs:"
        tail -20 "$LOG_FILE"
        exit 1
    fi
}

cmd_stop() {
    print_header "Stopping SEAA System"

    if ! is_running; then
        print_warning "System is not running"
        exit 0
    fi

    local pid=$(get_pid)
    print_info "Stopping process (PID: $pid)..."

    # Try graceful shutdown first
    if kill -TERM "$pid" 2>/dev/null; then
        print_info "Sent SIGTERM, waiting for graceful shutdown..."
        local count=0
        while is_running && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done

        if is_running; then
            print_warning "Graceful shutdown timeout, force killing..."
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi

    # Clean up PID file
    rm -f "$PID_FILE"

    # Verify it's stopped
    sleep 1
    if is_running; then
        print_error "Failed to stop system"
        exit 1
    fi

    print_success "System stopped"
}

cmd_restart() {
    print_header "Restarting SEAA System"

    if is_running; then
        cmd_stop
    fi

    sleep 1
    cmd_start
}

cmd_status() {
    print_header "SEAA System Status"

    # Check if running
    if is_running; then
        print_success "System is RUNNING"
        echo "PID: $(get_pid)"
    else
        print_error "System is NOT RUNNING"
    fi

    echo ""

    # Check ports
    print_info "Port Status:"
    if lsof -i ":$MAIN_PORT" > /dev/null 2>&1; then
        print_success "API port $MAIN_PORT: OPEN"
    else
        print_warning "API port $MAIN_PORT: CLOSED"
    fi

    if lsof -i ":$OLLAMA_PORT" > /dev/null 2>&1; then
        print_success "Ollama port $OLLAMA_PORT: OPEN"
    else
        print_warning "Ollama port $OLLAMA_PORT: CLOSED"
    fi

    echo ""

    # API health check
    if is_running; then
        print_info "System Health Check:"
        if curl -s http://localhost:$MAIN_PORT/api/status > /dev/null 2>&1; then
            local health=$(curl -s http://localhost:$MAIN_PORT/api/status | grep -o '"status":"[^"]*"' || echo '"status":"unknown"')
            print_success "API responding: $health"
        else
            print_warning "API not responding"
        fi
    fi
}

cmd_logs() {
    print_header "SEAA System Logs"

    if [ ! -f "$LOG_FILE" ]; then
        print_warning "No log file found at $LOG_FILE"
        exit 1
    fi

    # Check if follow flag is set
    if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
        tail -f "$LOG_FILE"
    else
        # Show last 50 lines
        tail -50 "$LOG_FILE"
    fi
}

cmd_watch() {
    print_header "SEAA System Events (Live Stream)"

    check_venv
    activate_venv

    if ! is_running; then
        print_error "System is not running"
        exit 1
    fi

    $PYTHON_CMD main.py watch
}

cmd_health() {
    print_header "SEAA System Health Check"

    check_venv
    activate_venv

    if ! is_running; then
        print_error "System is not running"
        exit 1
    fi

    $PYTHON_CMD main.py status
}

cmd_organs() {
    print_header "SEAA System Organs"

    check_venv
    activate_venv

    if ! is_running; then
        print_error "System is not running"
        exit 1
    fi

    $PYTHON_CMD main.py organs
}

cmd_goals() {
    print_header "SEAA System Goals"

    check_venv
    activate_venv

    if ! is_running; then
        print_error "System is not running"
        exit 1
    fi

    $PYTHON_CMD main.py goals
}

cmd_failures() {
    print_header "SEAA System Failures"

    check_venv
    activate_venv

    if ! is_running; then
        print_error "System is not running"
        exit 1
    fi

    $PYTHON_CMD main.py failures
}

################################################################################
# Commands: Utilities
################################################################################

cmd_ollama_check() {
    print_header "Ollama Status Check"

    if lsof -i ":$OLLAMA_PORT" > /dev/null 2>&1; then
        print_success "Ollama is running on port $OLLAMA_PORT"

        # Try to get models
        if command -v curl > /dev/null; then
            print_info "Available models:"
            curl -s "http://localhost:$OLLAMA_PORT/api/tags" 2>/dev/null | python3 -m json.tool 2>/dev/null | head -20 || print_warning "Could not fetch models"
        fi
    else
        print_error "Ollama is NOT running on port $OLLAMA_PORT"
        print_info "Start Ollama with: ollama serve"
    fi
}

cmd_ports() {
    print_header "Port Usage Check"

    echo "Checking common ports used by SEAA..."
    echo ""

    local ports=("8000" "8001" "3000" "11434" "5432")

    for port in "${ports[@]}"; do
        if lsof -i ":$port" > /dev/null 2>&1; then
            print_success "Port $port: IN USE"
            lsof -i ":$port" | tail -1 | awk '{print "  " $1 " (PID: " $2 ")"}'
        else
            print_info "Port $port: available"
        fi
    done
}

cmd_reset() {
    print_header "System Reset"

    check_venv
    activate_venv

    if is_running; then
        print_warning "Stopping system before reset..."
        cmd_stop
    fi

    print_warning "This will reset system state but preserve instance identity"
    read -p "Continue? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Reset cancelled"
        exit 0
    fi

    $PYTHON_CMD main.py --reset

    print_success "System reset complete"
    print_info "Instance identity preserved in .identity.json"
}

cmd_interactive() {
    print_header "SEAA Interactive Mode"

    check_venv
    activate_venv

    $PYTHON_CMD main.py -i
}

cmd_api_test() {
    print_header "API Connectivity Test"

    if ! is_running; then
        print_error "System is not running"
        exit 1
    fi

    echo "Testing API endpoints..."
    echo ""

    local endpoints=(
        "status"
        "organs"
        "identity"
        "goals"
        "timeline"
        "failures"
    )

    for endpoint in "${endpoints[@]}"; do
        if curl -s "http://localhost:$MAIN_PORT/api/$endpoint" > /dev/null 2>&1; then
            print_success "GET /api/$endpoint: OK"
        else
            print_error "GET /api/$endpoint: FAILED"
        fi
    done
}

################################################################################
# Commands: Documentation & Help
################################################################################

cmd_help() {
    cat << 'EOF'

╔════════════════════════════════════════════════════════════════╗
║                    SEAA Management Script                      ║
║              Manage SEAA system operations easily               ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  ./manage.sh [COMMAND] [OPTIONS]

CORE COMMANDS:
  start                  Start the SEAA system
  stop                   Stop the SEAA system gracefully
  restart                Restart the system
  status                 Show system status and port usage

MONITORING COMMANDS:
  logs [-f|--follow]     Show system logs (use -f to follow in real-time)
  watch                  Stream live system events
  health                 Get detailed system health information
  organs                 List all organs and their status
  goals                  Show goal satisfaction progress
  failures               View system failure history

UTILITY COMMANDS:
  ollama-check          Check Ollama status and available models
  ports                 Show port usage for all SEAA ports
  reset                 Reset system state (keeps instance identity)
  interactive           Start interactive REPL mode
  api-test              Test API endpoint connectivity

HELP:
  help                  Show this help message
  version               Show version information

EXAMPLES:
  # Start the system
  ./manage.sh start

  # Check status
  ./manage.sh status

  # Follow logs in real-time
  ./manage.sh logs -f

  # Stream live events
  ./manage.sh watch

  # Check system health
  ./manage.sh health

  # Restart the system
  ./manage.sh restart

  # Check Ollama
  ./manage.sh ollama-check

ENVIRONMENT VARIABLES:
  SEAA_PORT             API port (default: 8000)
  OLLAMA_PORT          Ollama port (default: 11434)
  PYTHON_CMD           Python command (default: python3)

EXIT CODES:
  0                     Success
  1                     Error
  2                     System not running (when required)

For more information, see: docs/guides/TROUBLESHOOTING.md

EOF
}

cmd_version() {
    echo "SEAA Management Script v1.0.0"
    echo "SEAA System: Self-Evolving Autonomous Agent"
    echo ""
    echo "Repository: https://github.com/nranjan2code/sutraworks-SEAAM"
    echo "Documentation: docs/README.md"
}

################################################################################
# Main Command Router
################################################################################

main() {
    local cmd="${1:-help}"

    case "$cmd" in
        # Core commands
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;

        # Monitoring
        logs)
            cmd_logs "$2"
            ;;
        watch)
            cmd_watch
            ;;
        health)
            cmd_health
            ;;
        organs)
            cmd_organs
            ;;
        goals)
            cmd_goals
            ;;
        failures)
            cmd_failures
            ;;

        # Utilities
        ollama-check)
            cmd_ollama_check
            ;;
        ports)
            cmd_ports
            ;;
        reset)
            cmd_reset
            ;;
        interactive)
            cmd_interactive
            ;;
        api-test)
            cmd_api_test
            ;;

        # Help
        help|--help|-h)
            cmd_help
            ;;
        version|--version|-v)
            cmd_version
            ;;

        *)
            print_error "Unknown command: $cmd"
            echo ""
            echo "Run './manage.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
