Kuberctl and all others
`curl -LO -k https://dl.k8s.io/release/$(curl -L -s -k https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl`
`sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl`
`curl -LO -k https://dl.k8s.io/release/$(curl -L -s -k https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubeadm`
`sudo install -o root -g root -m 0755 kubeadm /usr/local/bin/kubeadm`

`curl -LO -k https://dl.k8s.io/release/$(curl -L -s -k https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubelet`
`sudo install -o root -g root -m 0755 kubelet /usr/local/bin/kubelet`

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet
```

cd /etc/docker
sudo nano daemon.json

```json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "insecure-registries": ["192.168.253.78:5000"]
}
```

You clearly have the exact cause of the issue now:

- **You installed kubelet manually** using the binary (`curl`, then `install`) instead of using a package manager (`apt`).
- When installing kubelet this way, it does **not automatically provide the required systemd unit file (`kubelet.service`)**.

---

## 🚩 **How to properly fix it (clearly explained): - kubelet service installation**

Since you've manually installed `kubelet`, you'll also need to **explicitly create the systemd service file** for it.

Follow these exact steps carefully:

---

### ✅ **Step 1: Clearly verify `kubelet` binary location**

First, ensure your kubelet binary exists correctly:

```bash
which kubelet
```

It should clearly show:
```
/usr/local/bin/kubelet
```

---

### ✅ **Step 2: Create kubelet systemd file manually and explicitly**

Run exactly these commands to create the required service file clearly:

```bash
sudo tee /etc/systemd/system/kubelet.service <<EOF
[Unit]
Description=kubelet: The Kubernetes Node Agent
Documentation=https://kubernetes.io/docs/home/
After=docker.service network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/kubelet
Restart=always
RestartSec=10
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
EOF
```

---

### ✅ **Step 3: Reload systemd clearly and enable kubelet**

Run these commands clearly:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kubelet # Created symlink /etc/systemd/system/multi-user.target.wants/kubelet.service → /etc/systemd/system/kubelet.service.
sudo systemctl start kubelet
```

---

### ✅ **Step 4: Check kubelet status explicitly**

Run clearly to confirm:

```bash
sudo systemctl status kubelet
```

It must clearly show:
```
Active: active (running)
```

---

## 🚩 **Important:**  

Since you're manually installing binaries, you'll also need to ensure you manually install other Kubernetes components (`kubeadm` and `kubectl`) similarly:

Example:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubeadm"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

sudo install -o root -g root -m 0755 kubeadm /usr/local/bin/kubeadm
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

---

## ✅ **Clear and Safe final summary:**

Your error was because manual installation via binaries **does not include systemd files by default**.

Creating `kubelet.service` explicitly, as shown above, clearly resolves your problem:

- ✅ You manually create a `kubelet.service`.
- ✅ You enable/start it clearly via `systemctl`.
- ✅ Kubernetes (`kubeadm`) will now function normally.

---


### So we got error like

```
● kubelet.service - kubelet: The Kubernetes Node Agent
     Loaded: loaded (/etc/systemd/system/kubelet.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Fri 2025-03-28 13:17:11 IST; 5s ago
       Docs: https://kubernetes.io/docs/home/
    Process: 4162991 ExecStart=/usr/local/bin/kubelet (code=exited, status=1/FAILURE)
   Main PID: 4162991 (code=exited, status=1/FAILURE)
        CPU: 43ms
```

now:

we need to use cri-docker

`sudo dpkg -i cri-dockerd_0.3.16.3-0.debian-bullseye_amd64.deb`

```bash
sudo systemctl start cri-docker
sudo systemctl enable cri-docker
sudo systemctl status cri-docker
```