#!/bin/bash
# check_gpu_processes.sh

echo "=== GPU PROCESS ANALYZER ==="
echo ""

# Lấy list PIDs từ nvidia-smi
PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)

for PID in $PIDS; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "PID: $PID"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # User và basic info
    echo "👤 USER & PROCESS:"
    ps -p $PID -o user,pid,ppid,%cpu,%mem,etime,cmd --no-headers
    echo ""
    
    # Working directory
    echo "📁 WORKING DIR:"
    readlink -f /proc/$PID/cwd 2>/dev/null || echo "Permission denied"
    echo ""
    
    # Command line đầy đủ
    echo "⚙️  FULL COMMAND:"
    cat /proc/$PID/cmdline 2>/dev/null | tr '\0' ' ' || echo "Permission denied"
    echo ""
    echo ""
    
    # Network ports (nếu có)
    echo "🌐 LISTENING PORTS:"
    sudo netstat -tulpn 2>/dev/null | grep $PID || echo "No ports found"
    echo ""
    
    echo ""
done