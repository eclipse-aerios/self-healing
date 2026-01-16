import asyncio

from scenarios import (
    cpu_power,
    sensor_failure,
    network_protocol_violation,
    link_quality_issues,
    communication_failure_indication
)

async def main():
    print("Starting self-healing module...")

    tasks = [
        asyncio.create_task(cpu_power.monitor_cpu_power()),
        # asyncio.create_task(sensor_failure.monitor_sensor()),
        # asyncio.create_task(network_protocol_violation.enable_monitoring_agent()),
        # asyncio.create_task(link_quality_issues.monitor_link_quality()),
        # asyncio.create_task(communication_failure_indication.monitor_communication()),
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())