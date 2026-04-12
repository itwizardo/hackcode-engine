---
name: cheatsheet-default-creds
description: Common default credentials for services, admin panels, databases, and network devices
---

# Common Default Credentials

## Web Applications
| Application | Username | Password |
|-------------|----------|----------|
| WordPress | admin | admin |
| Joomla | admin | admin |
| Drupal | admin | admin |
| phpMyAdmin | root | (empty) |
| Tomcat | tomcat | tomcat |
| Tomcat | admin | admin |
| Jenkins | admin | admin |
| Grafana | admin | admin |
| Kibana | elastic | changeme |
| Webmin | root | (system password) |
| Nagios | nagiosadmin | nagios |
| Zabbix | Admin | zabbix |

## Databases
| Database | Username | Password |
|----------|----------|----------|
| MySQL | root | (empty) |
| MySQL | root | root |
| PostgreSQL | postgres | postgres |
| MongoDB | admin | admin |
| Redis | (none) | (none) |
| MSSQL | sa | sa |
| Oracle | system | oracle |

## Network/Infrastructure
| Device | Username | Password |
|--------|----------|----------|
| Cisco | admin | admin |
| Cisco | cisco | cisco |
| Netgear | admin | password |
| TP-Link | admin | admin |
| D-Link | admin | (empty) |
| MikroTik | admin | (empty) |
| Ubiquiti | ubnt | ubnt |
| pfSense | admin | pfsense |
| FortiGate | admin | (empty) |

## SSH / FTP
| Service | Username | Password |
|---------|----------|----------|
| SSH | root | toor |
| SSH | admin | admin |
| FTP | anonymous | (any) |
| FTP | ftp | ftp |

## IoT / Embedded
| Device | Username | Password |
|--------|----------|----------|
| Raspberry Pi | pi | raspberry |
| Default Linux | root | root |
| IP Camera | admin | admin |
| IP Camera | admin | 12345 |

Use `hydra` to test these credentials against discovered services.
