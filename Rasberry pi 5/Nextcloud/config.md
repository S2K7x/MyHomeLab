# Nextcloud on Raspberry Pi 5 with External SSD

A robust, high-performance self-hosted cloud setup using Docker, MariaDB, and Redis.

## 📌 Overview

This project provides a "disposable OS" architecture. By moving 100% of the persistent data to an external SSD and using **Labels** for mounting, the Raspberry Pi's SD card remains easily replaceable without risking data loss.

### Hardware Used

* **Raspberry Pi 5**
* **External 1TB SSD** (USB 3.0 / UASP compatible)
* **microSD Card** (For Raspberry Pi OS only)

---

## 🛠 1. SSD Preparation & Mounting

We use **LABELS** instead of UUIDs or device names (`/dev/sda1`). This ensures that if you change USB ports, the system still finds the data correctly.

### Format the SSD

```bash
# Identify your drive (usually sda)
lsblk

# Create an ext4 partition with the label 'NEXTCLOUD_DATA'
sudo mkfs.ext4 -L NEXTCLOUD_DATA /dev/sda1

```

### Configure Persistent Mounting

Create the mount point and update the filesystem table:

```bash
sudo mkdir -p /mnt/nextcloud_data

# Add this line to /etc/fstab
echo 'LABEL=NEXTCLOUD_DATA  /mnt/nextcloud_data  ext4  defaults,noatime  0  2' | sudo tee -a /etc/fstab

# Mount the drive
sudo mount -a

```

---

## 📂 2. Directory Structure & Permissions

Nextcloud requires specific ownership for the web server to write data. We use UID `33` (the default `www-data` user inside the Nextcloud Docker image).

```bash
# Create application folders on the SSD
sudo mkdir -p /mnt/nextcloud_data/nextcloud/html
sudo mkdir -p /mnt/nextcloud_data/nextcloud/data
sudo mkdir -p /mnt/nextcloud_data/db
sudo mkdir -p /mnt/nextcloud_data/redis

# Set permissions for the Nextcloud app
sudo chown -R 33:33 /mnt/nextcloud_data/nextcloud

```

---

## 🐳 3. Docker Deployment

### Docker Compose Configuration

Create a `docker-compose.yml` file in your home directory (e.g., `~/nextcloud-pi/`).

```yaml
services:
  db:
    image: mariadb:10.11
    container_name: nextcloud_db
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    volumes:
      - /mnt/nextcloud_data/db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=your_strong_password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=your_database_password
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: nextcloud_redis
    restart: unless-stopped

  app:
    image: nextcloud:stable
    container_name: nextcloud_app
    ports:
      - 8080:80
    depends_on:
      - db
      - redis
    volumes:
      - /mnt/nextcloud_data/nextcloud/html:/var/www/html
      - /mnt/nextcloud_data/nextcloud/data:/var/www/html/data
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=your_database_password
      - REDIS_HOST=redis
    restart: unless-stopped

```

### Start the Stack

```bash
docker compose up -d

```

Access the setup wizard at `http://<your-pi-ip>:8080`.

---

## 🔄 4. Maintenance: Replacing the SSD

If you need to upgrade to a larger SSD or replace a failing drive, follow this "zero-reconfiguration" procedure:

1. **Stop Containers:** `docker compose down`
2. **Prepare New Drive:** Format the new SSD with a temporary label:
```bash
sudo mkfs.ext4 -L NEXTCLOUD_NEW /dev/sdb1
sudo mkdir -p /mnt/new_ssd
sudo mount /dev/sdb1 /mnt/new_ssd

```


3. **Sync Data:**
```bash
sudo rsync -avh --progress /mnt/nextcloud_data/ /mnt/new_ssd/

```


4. **Swap Labels:**
```bash
# Rename old drive
sudo e2label /dev/sda1 NEXTCLOUD_OLD
# Rename new drive to the production label
sudo e2label /dev/sdb1 NEXTCLOUD_DATA

```


5. **Restart:** Unplug the old drive and run `docker compose up -d`.

---

## 🚀 5. Performance Tips for RPi 5

* **Redis:** Included in this setup to handle file locking and memory caching, significantly speeding up the interface.
* **Noatime:** The `noatime` mount option in `fstab` reduces SSD wear and improves speed by not writing access times for every file read.

---