# start_services.ps1

# Start NATS server (with full path)
$natsPath = (Get-Command nats-server).Source
Start-Process -NoNewWindow -FilePath $natsPath

# Start microservices
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "order_service/app.py"
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "inventory_service/consumer.py"
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "payment_service/consumer.py"

# Keep window open
Read-Host -Prompt "Press Enter to exit"