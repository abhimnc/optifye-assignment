output "instance_ip" {
  value = aws_instance.kafka.public_ip
}
