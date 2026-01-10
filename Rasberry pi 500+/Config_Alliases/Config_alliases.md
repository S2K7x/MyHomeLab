## 📁 **Création et installation du fichier d'aliases :**

1. **Créez le fichier d'aliases :**
   ```bash
   nano ~/.ctf_aliases
   ```
   Copiez-collez le contenu ci-dessus, puis : `Ctrl+X`, `Y`, `Enter`

2. **Ajoutez cette ligne à la fin de votre `.bashrc` :**
   ```bash
   echo "source ~/.ctf_aliases" >> ~/.bashrc
   ```

3. **Appliquez les changements :**
   ```bash
   source ~/.bashrc
   ```

## 🚀 **Commandes disponibles après installation :**

### **Navigation rapide :**
```bash
tools          # Va dans ~/tools
wordlists      # Va dans ~/wordlists
windows-tools  # Va dans ~/tools/windows
peass-ng       # Va dans ~/tools/peass-ng
ligolo-ng      # Va dans ~/tools/ligolo-ng
```

### **Commandes raccourcies :**
```bash
subf           # Lance subfinder
httpx          # Lance httpx
wayback        # Lance waybackurls
dirsearch      # Lance dirsearch
linpeas        # Lance LinPEAS (script)
linpeas64      # Lance LinPEAS (binaire ARM64)
ligolo-agent   # Lance l'agent Ligolo-ng
ligolo-proxy   # Lance le proxy Ligolo-ng
```

### **Commandes combinées pratiques :**
```bash
scan-ports example.com     # Scan complet des ports
quick-scan example.com     # Scan rapide
dir-fuzz http://example.com # Fuzzing de répertoires
subdomain-enum example.com # Énumération de sous-domaines
```

### **Utilitaires :**
```bash
check-tools     # Vérifie les outils installés
update-go-tools # Met à jour tous les outils Go
ctf-help        # Affiche l'aide avec toutes les commandes
```

## 🎯 **Exemples d'utilisation :**

1. **Énumération complète :**
   ```bash
   subf -d target.com | httpx -silent | nuclei -t ~/nuclei-templates/
   ```

2. **Scan rapide :**
   ```bash
   quick-scan 192.168.1.1
   ```

3. **Fuzzing de répertoires :**
   ```bash
   dir-fuzz http://target.com -w ~/wordlists/SecLists/Discovery/Web-Content/common.txt
   ```

4. **Énumération Linux :**
   ```bash
   linpeas
   # ou
   linpeas64
   ```

5. **Vérifier l'installation :**
   ```bash
   check-tools
   ```