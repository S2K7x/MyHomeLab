#!/bin/bash

# ============================================
# CTF/Pentest/Bug Bounty Installation Script
# Ubuntu aarch64 - Tools Installation Automatisée
# ============================================

# Configuration
TOOLS_DIR="$HOME/tools"
WORDLISTS_DIR="$HOME/wordlists"
WINDOWS_TOOLS_DIR="$TOOLS_DIR/windows"
PEASS_DIR="$TOOLS_DIR/peass-ng"
LIGOLO_DIR="$TOOLS_DIR/ligolo-ng"
LOG_FILE="$HOME/tools_installation.log"
ERROR_LOG_FILE="$HOME/tools_installation_errors.log"

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# Fonctions utilitaires
# ============================================

log_message() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    echo "$(date): $1" >> "$ERROR_LOG_FILE"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

check_architecture() {
    ARCH=$(uname -m)
    if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
        log_warning "Architecture détectée: $ARCH"
        log_warning "Ce script est optimisé pour aarch64/arm64"
        read -p "Voulez-vous continuer quand même? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_message "Architecture aarch64 confirmée"
    fi
}

install_if_missing() {
    local package=$1
    if dpkg -l | grep -q "^ii  $package "; then
        log_message "$package est déjà installé"
    else
        log_message "Installation de $package..."
        sudo apt-get install -y "$package" 2>> "$ERROR_LOG_FILE"
        if [ $? -eq 0 ]; then
            log_success "$package installé avec succès"
        else
            log_error "Échec de l'installation de $package"
            return 1
        fi
    fi
    return 0
}

# ============================================
# Configuration initiale
# ============================================

clear
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Installation Tools CTF/Pentest/Bug Bounty${NC}"
echo -e "${GREEN}        Ubuntu aarch64${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Vérification de l'architecture
check_architecture

# Nettoyer les anciens logs
> "$LOG_FILE"
> "$ERROR_LOG_FILE"

log_message "Début de l'installation - $(date)"
log_message "Logs: $LOG_FILE"
log_message "Logs d'erreurs: $ERROR_LOG_FILE"

# Création des répertoires
log_message "Création des répertoires de travail..."
mkdir -p "$TOOLS_DIR"
mkdir -p "$WORDLISTS_DIR"
mkdir -p "$WINDOWS_TOOLS_DIR"
mkdir -p "$PEASS_DIR"
mkdir -p "$LIGOLO_DIR"

# ============================================
# 1. SYSTEM PREREQUISITES
# ============================================

log_message "==========================================="
log_message "1. INSTALLATION DES PRÉREQUIS SYSTÈME"
log_message "==========================================="

# Mise à jour du système
log_message "Mise à jour des paquets système..."
sudo apt-get update 2>> "$ERROR_LOG_FILE"
sudo apt-get upgrade -y 2>> "$ERROR_LOG_FILE"

# Installation des paquets essentiels
ESSENTIAL_PACKAGES=(
    "git"
    "curl"
    "wget"
    "python3"
    "python3-pip"
    "python3-venv"
    "python3-dev"
    "build-essential"
    "ruby"
    "ruby-dev"
    "jq"
    "make"
    "gcc"
    "g++"
    "libpcap-dev"
    "libssl-dev"
    "libffi-dev"
    "zlib1g-dev"
    "libsqlite3-dev"
    "libreadline-dev"
    "libbz2-dev"
    "libncursesw5-dev"
    "libgdbm-dev"
    "liblzma-dev"
    "tk-dev"
    "libdb-dev"
    "uuid-dev"
    "p7zip-full"
)

for package in "${ESSENTIAL_PACKAGES[@]}"; do
    install_if_missing "$package"
done

# ============================================
# 2. INSTALLATION DE GO (version spécifique)
# ============================================

log_message "==========================================="
log_message "2. INSTALLATION DE GO 1.24+"
log_message "==========================================="

# Vérifier si Go est déjà installé
if check_command "go"; then
    CURRENT_GO_VERSION=$(go version | grep -o 'go[0-9]\+\.[0-9]\+')
    log_message "Go est déjà installé: $CURRENT_GO_VERSION"
    
    # Vérifier si la version est suffisante
    if [[ "$CURRENT_GO_VERSION" =~ go([0-9]+)\.([0-9]+) ]]; then
        MAJOR=${BASH_REMATCH[1]}
        MINOR=${BASH_REMATCH[2]}
        if [ "$MAJOR" -eq 1 ] && [ "$MINOR" -ge 24 ]; then
            log_success "Version de Go suffisante (1.24+)"
        else
            log_warning "Version de Go insuffisante, installation de la dernière version..."
            # Installation de la dernière version
            GO_VERSION="1.24.0"
            log_message "Téléchargement de Go $GO_VERSION pour linux/arm64..."
            wget "https://go.dev/dl/go${GO_VERSION}.linux-arm64.tar.gz" -O /tmp/go.tar.gz 2>> "$ERROR_LOG_FILE"
            if [ $? -eq 0 ]; then
                sudo rm -rf /usr/local/go
                sudo tar -C /usr/local -xzf /tmp/go.tar.gz
                rm /tmp/go.tar.gz
                log_success "Go $GO_VERSION installé"
            else
                log_error "Échec du téléchargement de Go"
            fi
        fi
    fi
else
    # Installation de Go depuis le site officiel
    GO_VERSION="1.24.0"
    log_message "Installation de Go $GO_VERSION..."
    wget "https://go.dev/dl/go${GO_VERSION}.linux-arm64.tar.gz" -O /tmp/go.tar.gz 2>> "$ERROR_LOG_FILE"
    
    if [ $? -eq 0 ]; then
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf /tmp/go.tar.gz
        rm /tmp/go.tar.gz
        log_success "Go $GO_VERSION installé"
    else
        log_error "Échec de l'installation de Go"
        log_message "Tentative avec le dépôt Ubuntu..."
        sudo add-apt-repository ppa:longsleep/golang-backports -y
        sudo apt-get update
        install_if_missing "golang-go"
    fi
fi

# Configuration du PATH pour Go
if [ -d "/usr/local/go/bin" ] && [[ ":$PATH:" != *":/usr/local/go/bin:"* ]]; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
    log_message "PATH de Go configuré"
fi

# Vérification finale de Go
if check_command "go"; then
    GO_PATH=$(go env GOPATH 2>/dev/null)
    if [ -n "$GO_PATH" ] && [[ ":$PATH:" != *":$GO_PATH/bin:"* ]]; then
        echo "export PATH=\$PATH:$GO_PATH/bin" >> ~/.bashrc
        export PATH=$PATH:$GO_PATH/bin
    fi
    log_success "Go configuré: $(go version)"
else
    log_error "Go n'est pas installé correctement"
    exit 1
fi

# ============================================
# 3. INSTALLATION DES OUTILS DE RECONNAISSANCE
# ============================================

log_message "==========================================="
log_message "3. OUTILS DE RECONNAISSANCE"
log_message "==========================================="

# subfinder
log_message "Installation de subfinder..."
if check_command "subfinder"; then
    log_message "subfinder déjà installé"
else
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "subfinder installé"
    else
        log_error "Échec de l'installation de subfinder"
    fi
fi

# assetfinder
log_message "Installation de assetfinder..."
if check_command "assetfinder"; then
    log_message "assetfinder déjà installé"
else
    go get -u github.com/tomnomnom/assetfinder 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "assetfinder installé"
    else
        log_error "Échec de l'installation de assetfinder"
    fi
fi

# httpx
log_message "Installation de httpx..."
if check_command "httpx"; then
    log_message "httpx déjà installé"
else
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "httpx installé"
    else
        log_error "Échec de l'installation de httpx"
    fi
fi

# waybackurls
log_message "Installation de waybackurls..."
if check_command "waybackurls"; then
    log_message "waybackurls déjà installé"
else
    go install github.com/tomnomnom/waybackurls@latest 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "waybackurls installé"
    else
        log_error "Échec de l'installation de waybackurls"
    fi
fi

# theHarvester
log_message "Installation de theHarvester..."
if [ -d "$TOOLS_DIR/theHarvester" ]; then
    log_message "theHarvester déjà installé"
else
    cd "$TOOLS_DIR"
    git clone https://github.com/laramies/theHarvester.git 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        cd theHarvester
        python3 -m venv venv 2>> "$ERROR_LOG_FILE"
        source venv/bin/activate
        pip3 install -r requirements.txt 2>> "$ERROR_LOG_FILE"
        deactivate
        log_success "theHarvester installé"
    else
        log_error "Échec de l'installation de theHarvester"
    fi
fi

# recon-ng
log_message "Installation de recon-ng..."
if [ -d "$TOOLS_DIR/recon-ng" ]; then
    log_message "recon-ng déjà installé"
else
    cd "$TOOLS_DIR"
    git clone https://github.com/lanmaster53/recon-ng.git 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        cd recon-ng
        pip3 install -r REQUIREMENTS 2>> "$ERROR_LOG_FILE"
        log_success "recon-ng installé"
    else
        log_error "Échec de l'installation de recon-ng"
    fi
fi

# ============================================
# 4. OUTILS DE SCANNING RÉSEAU
# ============================================

log_message "==========================================="
log_message "4. OUTILS DE SCANNING RÉSEAU"
log_message "==========================================="

# Nmap
log_message "Installation de Nmap..."
install_if_missing "nmap"

# masscan
log_message "Installation de masscan..."
if check_command "masscan"; then
    log_message "masscan déjà installé"
else
    cd "$TOOLS_DIR"
    sudo apt-get -y install git gcc make libpcap-dev 2>> "$ERROR_LOG_FILE"
    git clone https://github.com/robertdavidgraham/masscan 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        cd masscan/
        make 2>> "$ERROR_LOG_FILE"
        if [ $? -eq 0 ]; then
            sudo make install 2>> "$ERROR_LOG_FILE"
            log_success "masscan installé"
        else
            log_error "Échec de la compilation de masscan"
        fi
    else
        log_error "Échec du clonage de masscan"
    fi
fi

# naabu
log_message "Installation de naabu..."
if check_command "naabu"; then
    log_message "naabu déjà installé"
else
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "naabu installé"
    else
        log_error "Échec de l'installation de naabu"
    fi
fi

# ============================================
# 5. OUTILS WEB / FUZZING
# ============================================

log_message "==========================================="
log_message "5. OUTILS WEB / FUZZING"
log_message "==========================================="

# ffuf
log_message "Installation de ffuf..."
if check_command "ffuf"; then
    log_message "ffuf déjà installé"
else
    go install github.com/ffuf/ffuf/v2@latest 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "ffuf installé"
    else
        log_error "Échec de l'installation de ffuf"
    fi
fi

# dirsearch
log_message "Installation de dirsearch..."
if [ -d "$TOOLS_DIR/dirsearch" ]; then
    log_message "dirsearch déjà installé"
else
    cd "$TOOLS_DIR"
    git clone https://github.com/maurosoria/dirsearch.git --depth 1 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "dirsearch installé"
    else
        log_error "Échec de l'installation de dirsearch"
    fi
fi

# nuclei
log_message "Installation de nuclei..."
if check_command "nuclei"; then
    log_message "nuclei déjà installé"
else
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "nuclei installé"
    else
        log_error "Échec de l'installation de nuclei"
    fi
fi

# sqlmap
log_message "Installation de sqlmap..."
if [ -d "$TOOLS_DIR/sqlmap-dev" ]; then
    log_message "sqlmap déjà installé"
else
    cd "$TOOLS_DIR"
    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "sqlmap installé"
    else
        log_error "Échec de l'installation de sqlmap"
    fi
fi

# ============================================
# 6. OUTILS DE REVERSE ENGINEERING / DEBUG
# ============================================

log_message "==========================================="
log_message "6. OUTILS REVERSE ENGINEERING / DEBUG"
log_message "==========================================="

# GDB
log_message "Installation de GDB..."
install_if_missing "gdb"

# ============================================
# 7. METASPLOIT FRAMEWORK
# ============================================

log_message "==========================================="
log_message "7. METASPLOIT FRAMEWORK"
log_message "==========================================="

if check_command "msfconsole"; then
    log_message "Metasploit déjà installé"
else
    log_message "Installation de Metasploit Framework..."
    curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > /tmp/msfinstall 2>> "$ERROR_LOG_FILE"
    
    if [ $? -eq 0 ]; then
        chmod 755 /tmp/msfinstall
        sudo /tmp/msfinstall 2>> "$ERROR_LOG_FILE"
        
        if [ $? -eq 0 ]; then
            log_success "Metasploit Framework installé"
            
            # Configuration de la base de données
            log_message "Configuration de la base de données Metasploit..."
            sudo systemctl start postgresql 2>> "$ERROR_LOG_FILE"
            sudo systemctl enable postgresql 2>> "$ERROR_LOG_FILE"
            
            # Initialisation de la base de données
            msfdb init 2>> "$ERROR_LOG_FILE"
            
        else
            log_error "Échec de l'installation de Metasploit"
        fi
        rm /tmp/msfinstall
    else
        log_error "Échec du téléchargement de l'installateur Metasploit"
    fi
fi

# ============================================
# 8. OUTILS DE BRUTE-FORCE
# ============================================

log_message "==========================================="
log_message "8. OUTILS DE BRUTE-FORCE"
log_message "==========================================="

# Hydra
log_message "Installation de Hydra..."
install_if_missing "hydra"

# ============================================
# 9. OUTILS WINDOWS / POST-EXPLOITATION
# ============================================

log_message "==========================================="
log_message "9. OUTILS WINDOWS / POST-EXPLOITATION"
log_message "==========================================="

# Mimikatz (version spécifique du 19/09/2022)
log_message "Téléchargement de Mimikatz 2.2.0-20220919..."
MIMIKATZ_URL="https://github.com/gentilkiwi/mimikatz/releases/download/2.2.0-20220919/mimikatz_trunk.zip"
MIMIKATZ_ZIP="$WINDOWS_TOOLS_DIR/mimikatz_trunk.zip"
MIMIKATZ_DIR="$WINDOWS_TOOLS_DIR/mimikatz"

if [ -d "$MIMIKATZ_DIR" ]; then
    log_message "Mimikatz déjà téléchargé"
else
    wget "$MIMIKATZ_URL" -O "$MIMIKATZ_ZIP" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        # Installation de 7zip pour extraction si nécessaire
        if ! check_command "7z"; then
            install_if_missing "p7zip-full"
        fi
        
        # Extraction de l'archive
        if check_command "7z"; then
            7z x "$MIMIKATZ_ZIP" -o"$MIMIKATZ_DIR" 2>> "$ERROR_LOG_FILE"
        else
            unzip "$MIMIKATZ_ZIP" -d "$MIMIKATZ_DIR" 2>> "$ERROR_LOG_FILE"
        fi
        
        if [ $? -eq 0 ]; then
            log_success "Mimikatz téléchargé et extrait dans $MIMIKATZ_DIR"
            rm "$MIMIKATZ_ZIP"
        else
            log_error "Échec de l'extraction de Mimikatz"
        fi
    else
        log_error "Échec du téléchargement de Mimikatz"
    fi
fi

# ============================================
# 10. OUTILS D'ÉNUMÉRATION PEASS-ng
# ============================================

log_message "==========================================="
log_message "10. OUTILS D'ÉNUMÉRATION PEASS-ng"
log_message "==========================================="

# Version spécifique de PEASS-ng
PEASS_VERSION="20260101-f70f6a79"
PEASS_BASE_URL="https://github.com/peass-ng/PEASS-ng/releases/download/$PEASS_VERSION"

# LinPEAS (Linux)
log_message "Téléchargement de LinPEAS..."
LINPEAS_SH="$PEASS_DIR/linpeas.sh"
LINPEAS_ARM64="$PEASS_DIR/linpeas_linux_arm64"

if [ ! -f "$LINPEAS_SH" ]; then
    wget "$PEASS_BASE_URL/linpeas.sh" -O "$LINPEAS_SH" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        chmod +x "$LINPEAS_SH"
        log_success "LinPEAS (script) téléchargé"
    else
        log_error "Échec du téléchargement de LinPEAS (script)"
    fi
else
    log_message "LinPEAS (script) déjà présent"
fi

if [ ! -f "$LINPEAS_ARM64" ]; then
    wget "$PEASS_BASE_URL/linpeas_linux_arm64" -O "$LINPEAS_ARM64" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        chmod +x "$LINPEAS_ARM64"
        log_success "LinPEAS (binaire ARM64) téléchargé"
    else
        log_error "Échec du téléchargement de LinPEAS (binaire ARM64)"
    fi
else
    log_message "LinPEAS (binaire ARM64) déjà présent"
fi

# WinPEAS (Windows)
log_message "Téléchargement de WinPEAS..."
WINPEAS_ANY="$WINDOWS_TOOLS_DIR/winPEASany.exe"
WINPEAS_X64="$WINDOWS_TOOLS_DIR/winPEASx64.exe"
WINPEAS_X86="$WINDOWS_TOOLS_DIR/winPEASx86.exe"
WINPEAS_BAT="$WINDOWS_TOOLS_DIR/winPEAS.bat"

if [ ! -f "$WINPEAS_ANY" ]; then
    wget "$PEASS_BASE_URL/winPEASany.exe" -O "$WINPEAS_ANY" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "WinPEASany.exe téléchargé"
    else
        log_error "Échec du téléchargement de WinPEASany.exe"
    fi
else
    log_message "WinPEASany.exe déjà présent"
fi

if [ ! -f "$WINPEAS_X64" ]; then
    wget "$PEASS_BASE_URL/winPEASx64.exe" -O "$WINPEAS_X64" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "WinPEASx64.exe téléchargé"
    else
        log_error "Échec du téléchargement de WinPEASx64.exe"
    fi
else
    log_message "WinPEASx64.exe déjà présent"
fi

if [ ! -f "$WINPEAS_X86" ]; then
    wget "$PEASS_BASE_URL/winPEASx86.exe" -O "$WINPEAS_X86" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "WinPEASx86.exe téléchargé"
    else
        log_error "Échec du téléchargement de WinPEASx86.exe"
    fi
else
    log_message "WinPEASx86.exe déjà présent"
fi

if [ ! -f "$WINPEAS_BAT" ]; then
    wget "$PEASS_BASE_URL/winPEAS.bat" -O "$WINPEAS_BAT" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        chmod +x "$WINPEAS_BAT"
        log_success "winPEAS.bat téléchargé"
    else
        log_error "Échec du téléchargement de winPEAS.bat"
    fi
else
    log_message "winPEAS.bat déjà présent"
fi

# ============================================
# 11. LIGOLO-NG (OUTIL DE PIVOTEMENT)
# ============================================

log_message "==========================================="
log_message "11. LIGOLO-NG (OUTIL DE PIVOTEMENT)"
log_message "==========================================="

# Version spécifique de Ligolo-ng
LIGOLO_VERSION="v0.8"
LIGOLO_BASE_URL="https://github.com/nicocha30/ligolo-ng/releases/download/$LIGOLO_VERSION"

# Téléchargement de l'agent et du proxy pour Linux ARM64
log_message "Téléchargement de Ligolo-ng Agent..."
LIGOLO_AGENT_TAR="/tmp/ligolo-ng_agent_linux_arm64.tar.gz"
LIGOLO_AGENT_URL="$LIGOLO_BASE_URL/ligolo-ng_agent_0.8_linux_arm64.tar.gz"

if [ ! -f "$LIGOLO_DIR/ligolo-ng_agent" ]; then
    wget "$LIGOLO_AGENT_URL" -O "$LIGOLO_AGENT_TAR" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        tar -xzf "$LIGOLO_AGENT_TAR" -C "$LIGOLO_DIR" 2>> "$ERROR_LOG_FILE"
        if [ $? -eq 0 ]; then
            # Renommer le binaire pour simplicité
            mv "$LIGOLO_DIR/ligolo-ng_agent_0.8_linux_arm64/ligolo-ng_agent" "$LIGOLO_DIR/ligolo-ng_agent" 2>> "$ERROR_LOG_FILE"
            rm -rf "$LIGOLO_DIR/ligolo-ng_agent_0.8_linux_arm64"
            chmod +x "$LIGOLO_DIR/ligolo-ng_agent"
            log_success "Ligolo-ng Agent téléchargé et installé"
        else
            log_error "Échec de l'extraction de Ligolo-ng Agent"
        fi
        rm "$LIGOLO_AGENT_TAR"
    else
        log_error "Échec du téléchargement de Ligolo-ng Agent"
    fi
else
    log_message "Ligolo-ng Agent déjà présent"
fi

log_message "Téléchargement de Ligolo-ng Proxy..."
LIGOLO_PROXY_TAR="/tmp/ligolo-ng_proxy_linux_arm64.tar.gz"
LIGOLO_PROXY_URL="$LIGOLO_BASE_URL/ligolo-ng_proxy_0.8_linux_arm64.tar.gz"

if [ ! -f "$LIGOLO_DIR/ligolo-ng_proxy" ]; then
    wget "$LIGOLO_PROXY_URL" -O "$LIGOLO_PROXY_TAR" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        tar -xzf "$LIGOLO_PROXY_TAR" -C "$LIGOLO_DIR" 2>> "$ERROR_LOG_FILE"
        if [ $? -eq 0 ]; then
            # Renommer le binaire pour simplicité
            mv "$LIGOLO_DIR/ligolo-ng_proxy_0.8_linux_arm64/ligolo-ng_proxy" "$LIGOLO_DIR/ligolo-ng_proxy" 2>> "$ERROR_LOG_FILE"
            rm -rf "$LIGOLO_DIR/ligolo-ng_proxy_0.8_linux_arm64"
            chmod +x "$LIGOLO_DIR/ligolo-ng_proxy"
            log_success "Ligolo-ng Proxy téléchargé et installé"
        else
            log_error "Échec de l'extraction de Ligolo-ng Proxy"
        fi
        rm "$LIGOLO_PROXY_TAR"
    else
        log_error "Échec du téléchargement de Ligolo-ng Proxy"
    fi
else
    log_message "Ligolo-ng Proxy déjà présent"
fi

# Téléchargement des binaires Windows pour Ligolo-ng
log_message "Téléchargement des binaires Windows de Ligolo-ng..."
LIGOLO_WIN_AMD64_URL="$LIGOLO_BASE_URL/ligolo-ng_agent_0.8_windows_amd64.zip"
LIGOLO_WIN_AMD64_ZIP="$WINDOWS_TOOLS_DIR/ligolo-ng_agent_windows_amd64.zip"

if [ ! -f "$WINDOWS_TOOLS_DIR/ligolo-ng_agent_amd64.exe" ]; then
    wget "$LIGOLO_WIN_AMD64_URL" -O "$LIGOLO_WIN_AMD64_ZIP" 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        if check_command "7z"; then
            7z x "$LIGOLO_WIN_AMD64_ZIP" -o"$WINDOWS_TOOLS_DIR" 2>> "$ERROR_LOG_FILE"
        else
            unzip "$LIGOLO_WIN_AMD64_ZIP" -d "$WINDOWS_TOOLS_DIR" 2>> "$ERROR_LOG_FILE"
        fi
        
        if [ $? -eq 0 ]; then
            # Renommer pour simplicité
            mv "$WINDOWS_TOOLS_DIR/ligolo-ng_agent_0.8_windows_amd64/ligolo-ng_agent.exe" "$WINDOWS_TOOLS_DIR/ligolo-ng_agent_amd64.exe" 2>> "$ERROR_LOG_FILE"
            rm -rf "$WINDOWS_TOOLS_DIR/ligolo-ng_agent_0.8_windows_amd64"
            log_success "Ligolo-ng Agent Windows (AMD64) téléchargé"
        else
            log_error "Échec de l'extraction de Ligolo-ng Agent Windows"
        fi
        rm "$LIGOLO_WIN_AMD64_ZIP"
    else
        log_error "Échec du téléchargement de Ligolo-ng Agent Windows"
    fi
else
    log_message "Ligolo-ng Agent Windows déjà présent"
fi

# ============================================
# 12. INSTALLATION DE WORDLISTS
# ============================================

log_message "==========================================="
log_message "12. TÉLÉCHARGEMENT DES WORDLISTS"
log_message "==========================================="

cd "$WORDLISTS_DIR"

# SecLists
if [ ! -d "$WORDLISTS_DIR/SecLists" ]; then
    log_message "Téléchargement de SecLists..."
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git 2>> "$ERROR_LOG_FILE"
    if [ $? -eq 0 ]; then
        log_success "SecLists téléchargé"
    else
        log_error "Échec du téléchargement de SecLists"
    fi
else
    log_message "SecLists déjà présent"
fi

# rockyou.txt
if [ ! -f "$WORDLISTS_DIR/rockyou.txt" ]; then
    log_message "Décompression de rockyou.txt..."
    if [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
        sudo gunzip -c /usr/share/wordlists/rockyou.txt.gz > "$WORDLISTS_DIR/rockyou.txt" 2>> "$ERROR_LOG_FILE"
        log_success "rockyou.txt décompressé"
    else
        log_warning "rockyou.txt.gz non trouvé, téléchargement..."
        wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O "$WORDLISTS_DIR/rockyou.txt" 2>> "$ERROR_LOG_FILE"
    fi
else
    log_message "rockyou.txt déjà présent"
fi

# ============================================
# 13. CONFIGURATION FINALE
# ============================================

log_message "==========================================="
log_message "13. CONFIGURATION FINALE"
log_message "==========================================="

# Création des alias utiles
log_message "Création des alias dans .bashrc..."

ALIASES=(
    "alias dirsearch='python3 $TOOLS_DIR/dirsearch/dirsearch.py'"
    "alias sqlmap='python3 $TOOLS_DIR/sqlmap-dev/sqlmap.py'"
    "alias theharvester='cd $TOOLS_DIR/theHarvester && source venv/bin/activate && python3 theHarvester.py'"
    "alias recon-ng='cd $TOOLS_DIR/recon-ng && python3 recon-ng'"
    "alias tools='cd $TOOLS_DIR'"
    "alias wordlists='cd $WORDLISTS_DIR'"
    "alias windows-tools='cd $WINDOWS_TOOLS_DIR'"
    "alias peass-ng='cd $PEASS_DIR'"
    "alias ligolo-ng='cd $LIGOLO_DIR'"
    "alias linpeas='bash $PEASS_DIR/linpeas.sh'"
    "alias linpeas64='$PEASS_DIR/linpeas_linux_arm64'"
    "alias ligolo-agent='$LIGOLO_DIR/ligolo-ng_agent'"
    "alias ligolo-proxy='$LIGOLO_DIR/ligolo-ng_proxy'"
)

for alias_line in "${ALIASES[@]}"; do
    if ! grep -Fxq "$alias_line" ~/.bashrc; then
        echo "$alias_line" >> ~/.bashrc
    fi
done

# Mise à jour du PATH
if [[ ":$PATH:" != *":$TOOLS_DIR:"* ]]; then
    echo "export PATH=\$PATH:$TOOLS_DIR" >> ~/.bashrc
fi

# Création d'un script de mise à jour
UPDATE_SCRIPT="$TOOLS_DIR/update_tools.sh"
cat > "$UPDATE_SCRIPT" << 'EOF'
#!/bin/bash
echo "Mise à jour des outils..."
cd ~/tools

# Mise à jour des dépôts git
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "Mise à jour de $dir"
        cd "$dir"
        git pull
        cd ..
    fi
done

# Mise à jour des outils Go
echo "Mise à jour des outils Go..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/ffuf/ffuf/v2@latest

# Mise à jour de PEASS-ng
echo "Vérification des nouvelles versions de PEASS-ng..."
LATEST_PEASS=$(curl -s https://api.github.com/repos/peass-ng/PEASS-ng/releases/latest | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4)
if [ ! -z "$LATEST_PEASS" ]; then
    echo "Nouvelle version disponible: $LATEST_PEASS"
    read -p "Voulez-vous mettre à jour PEASS-ng? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PEASS_URL="https://github.com/peass-ng/PEASS-ng/releases/download/$LATEST_PEASS"
        wget -q "$PEASS_URL/linpeas.sh" -O ~/tools/peass-ng/linpeas.sh
        wget -q "$PEASS_URL/linpeas_linux_arm64" -O ~/tools/peass-ng/linpeas_linux_arm64
        chmod +x ~/tools/peass-ng/linpeas.sh ~/tools/peass-ng/linpeas_linux_arm64
        echo "PEASS-ng mis à jour vers $LATEST_PEASS"
    fi
fi

echo "Mise à jour terminée!"
EOF

chmod +x "$UPDATE_SCRIPT"
log_success "Script de mise à jour créé: $UPDATE_SCRIPT"

# Création d'un script de vérification d'intégrité
INTEGRITY_SCRIPT="$TOOLS_DIR/check_tools.sh"
cat > "$INTEGRITY_SCRIPT" << 'EOF'
#!/bin/bash
echo "Vérification de l'intégrité des outils..."
echo ""

# Vérification des outils Go
GO_TOOLS=("subfinder" "assetfinder" "httpx" "waybackurls" "naabu" "nuclei" "ffuf")
echo "=== Outils Go ==="
for tool in "${GO_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "✓ $tool est installé"
    else
        echo -e "✗ $tool n'est pas installé"
    fi
done

echo ""
echo "=== Outils Python ==="
# Vérification des outils Python
if [ -d "$HOME/tools/theHarvester" ]; then
    echo "✓ theHarvester est installé"
else
    echo "✗ theHarvester n'est pas installé"
fi

if [ -d "$HOME/tools/recon-ng" ]; then
    echo "✓ recon-ng est installé"
else
    echo "✗ recon-ng n'est pas installé"
fi

if [ -d "$HOME/tools/dirsearch" ]; then
    echo "✓ dirsearch est installé"
else
    echo "✗ dirsearch n'est pas installé"
fi

if [ -d "$HOME/tools/sqlmap-dev" ]; then
    echo "✓ sqlmap est installé"
else
    echo "✗ sqlmap n'est pas installé"
fi

echo ""
echo "=== Outils système ==="
# Vérification des outils système
SYS_TOOLS=("nmap" "masscan" "hydra" "gdb" "msfconsole")
for tool in "${SYS_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "✓ $tool est installé"
    else
        echo -e "✗ $tool n'est pas installé"
    fi
done

echo ""
echo "=== Outils supplémentaires ==="
# Vérification des outils supplémentaires
if [ -f "$HOME/tools/peass-ng/linpeas.sh" ]; then
    echo "✓ LinPEAS est installé"
else
    echo "✗ LinPEAS n'est pas installé"
fi

if [ -f "$HOME/tools/ligolo-ng/ligolo-ng_agent" ]; then
    echo "✓ Ligolo-ng Agent est installé"
else
    echo "✗ Ligolo-ng Agent n'est pas installé"
fi

if [ -f "$HOME/tools/ligolo-ng/ligolo-ng_proxy" ]; then
    echo "✓ Ligolo-ng Proxy est installé"
else
    echo "✗ Ligolo-ng Proxy n'est pas installé"
fi

if [ -d "$HOME/tools/windows/mimikatz" ]; then
    echo "✓ Mimikatz est installé"
else
    echo "✗ Mimikatz n'est pas installé"
fi

echo ""
echo "=== Wordlists ==="
if [ -d "$HOME/wordlists/SecLists" ]; then
    echo "✓ SecLists est installé"
else
    echo "✗ SecLists n'est pas installé"
fi

if [ -f "$HOME/wordlists/rockyou.txt" ]; then
    echo "✓ rockyou.txt est installé"
else
    echo "✗ rockyou.txt n'est pas installé"
fi

echo ""
echo "Vérification terminée!"
EOF

chmod +x "$INTEGRITY_SCRIPT"
log_success "Script de vérification créé: $INTEGRITY_SCRIPT"

# ============================================
# FIN DU SCRIPT - RÉSUMÉ
# ============================================

log_message "==========================================="
log_message "INSTALLATION TERMINÉE"
log_message "==========================================="

log_success "Toutes les installations sont complétées!"
log_message ""
log_message "=== RÉSUMÉ DES INSTALLATIONS ==="
log_message "Répertoire des outils: $TOOLS_DIR"
log_message "Répertoire des wordlists: $WORDLISTS_DIR"
log_message "Répertoire des outils Windows: $WINDOWS_TOOLS_DIR"
log_message "Répertoire PEASS-ng: $PEASS_DIR"
log_message "Répertoire Ligolo-ng: $LIGOLO_DIR"
log_message "Log complet: $LOG_FILE"
log_message "Log d'erreurs: $ERROR_LOG_FILE"
log_message ""
log_message "=== OUTILS INSTALLÉS ==="
log_message "1. Reconnaissance: subfinder, assetfinder, httpx, waybackurls, theHarvester, recon-ng"
log_message "2. Scanning: nmap, masscan, naabu"
log_message "3. Web/Fuzzing: ffuf, dirsearch, nuclei, sqlmap"
log_message "4. Reverse Engineering: GDB"
log_message "5. Framework: Metasploit"
log_message "6. Brute-force: Hydra"
log_message "7. Windows/Post-exploitation: Mimikatz (2.2.0-20220919)"
log_message "8. Énumération: PEASS-ng (LinPEAS & WinPEAS)"
log_message "9. Pivotement: Ligolo-ng (Agent & Proxy)"
log_message ""
log_message "=== CONFIGURATION REQUISE ==="
log_message "1. Redémarrez votre terminal ou exécutez: source ~/.bashrc"
log_message "2. Pour Metasploit, exécutez: sudo systemctl start postgresql && msfconsole"
log_message "3. Pour vérifier l'installation: $INTEGRITY_SCRIPT"
log_message "4. Pour mettre à jour tous les outils: $UPDATE_SCRIPT"
log_message ""
log_message "=== ALIAS DISPONIBLES ==="
log_message "• linpeas    : Exécute LinPEAS (script)"
log_message "• linpeas64  : Exécute LinPEAS (binaire ARM64)"
log_message "• ligolo-agent : Lance Ligolo-ng Agent"
log_message "• ligolo-proxy : Lance Ligolo-ng Proxy"
log_message "• windows-tools : Accède aux outils Windows"
log_message "• peass-ng   : Accède aux outils PEASS-ng"
log_message "• ligolo-ng  : Accède aux outils Ligolo-ng"
log_message ""

# Vérification finale
if [ -s "$ERROR_LOG_FILE" ]; then
    ERROR_COUNT=$(wc -l < "$ERROR_LOG_FILE")
    log_warning "$ERROR_COUNT erreur(s) sont survenues pendant l'installation."
    log_warning "Consultez le fichier: $ERROR_LOG_FILE"
    log_message "Vous pouvez réexécuter le script pour tenter de réinstaller les outils manquants."
else
    log_success "Aucune erreur majeure détectée!"
fi

# Vérification rapide des outils essentiels
log_message ""
log_message "=== VÉRIFICATION RAPIDE ==="
ESSENTIAL_TOOLS=("subfinder" "nmap" "ffuf" "hydra")
for tool in "${ESSENTIAL_TOOLS[@]}"; do
    if check_command "$tool"; then
        log_success "$tool : OK"
    else
        log_error "$tool : NON INSTALLÉ"
    fi
done

log_message ""
log_message "=== TEMPS D'EXÉCUTION ==="
END_TIME=$(date)
log_message "Début: $(grep "Début de l'installation" "$LOG_FILE" | head -1 | cut -d'-' -f2-)"
log_message "Fin: $END_TIME"

log_message ""
log_message "Pour une vérification complète: ./check_tools.sh"
log_message "Installation terminée avec succès! 🎉"