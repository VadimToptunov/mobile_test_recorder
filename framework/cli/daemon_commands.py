"""Daemon command for JSON-RPC protocol server."""

import sys
import json
import logging
from typing import Dict, Any, Optional

import click

from framework.health import HealthChecker


logger = logging.getLogger(__name__)


class JSONRPCServer:
    """JSON-RPC 2.0 server for IDE plugin communication."""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.handlers = {
            "health/check": self.handle_health_check,
            # More handlers will be added in future phases
        }
    
    def handle_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request."""
        return self.health_checker.check()
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle JSON-RPC request.
        
        Args:
            request: JSON-RPC request dict
            
        Returns:
            JSON-RPC response dict
        """
        # Validate JSON-RPC version
        if request.get("jsonrpc") != "2.0":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: jsonrpc must be '2.0'"
                }
            }
        
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        # Check if method exists
        if method not in self.handlers:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        # Execute handler
        try:
            result = self.handlers[method](params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            logger.exception(f"Error handling {method}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run_stdio(self):
        """Run server using stdin/stdout."""
        logger.info("Starting JSON-RPC server (stdio mode)")
        
        # Send initial notification that we're ready
        ready_notification = {
            "jsonrpc": "2.0",
            "method": "notification/ready",
            "params": {
                "version": "0.5.0"
            }
        }
        print(json.dumps(ready_notification), flush=True)
        
        # Read requests from stdin line by line
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.exception("Unexpected error")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


@click.command(name="daemon")
@click.option(
    "--stdio",
    is_flag=True,
    default=True,
    help="Run in stdio mode (default)"
)
@click.option(
    "--tcp",
    type=int,
    help="Run in TCP mode on specified port (for debugging)"
)
def daemon_command(stdio: bool, tcp: Optional[int]):
    """
    Run JSON-RPC daemon for IDE plugin communication.
    
    Examples:
        observe daemon --stdio
        observe daemon --tcp 33333
    """
    server = JSONRPCServer()
    
    if tcp:
        click.echo(f"TCP mode not yet implemented. Use --stdio for now.", err=True)
        sys.exit(1)
    else:
        # Configure logging to stderr (won't interfere with JSON-RPC on stdout)
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            stream=sys.stderr
        )
        
        try:
            server.run_stdio()
        except KeyboardInterrupt:
            logger.info("Daemon shutting down")
            sys.exit(0)
        except Exception as e:
            logger.exception("Fatal error in daemon")
            sys.exit(1)
