#!/bin/bash
# n8n_command.sh - Command for n8n to run the processor
cd /home/jason/Documents/DatabaseAdvancedTokenizer/MinimalistRagIntake
nohup ./processor-background.sh "{{ $('Limit').first().json.FolderName }}" "{{ $json.executionMode || 'test' }}" > /tmp/processor_command.log 2>&1 &
echo "Processor started in background with PID: $!" 