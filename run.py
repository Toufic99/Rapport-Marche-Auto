"""
🚗 CAR ANALYTICS - MENU PRINCIPAL
==================================
Lance ce fichier pour gérer ton scraper facilement !

Usage: python run.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Aller dans le bon dossier
os.chdir(Path(__file__).parent)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear_screen()
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  🚗 CAR ANALYTICS                            ║
║                  Menu Principal                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   [1] 🔄 Scraper MAINTENANT (choisir pages/annonces)         ║
║                                                              ║
║   [2] ⏰ Programmer scraping AUTOMATIQUE                      ║
║                                                              ║
║   [3] 📊 Voir les STATISTIQUES de la base                    ║
║                                                              ║
║   [4] 📄 Générer RAPPORT HTML                                ║
║                                                              ║
║   [5] 🌐 Ouvrir l'API en ligne                               ║
║                                                              ║
║   [6] 📤 Pousser vers GitHub (mettre à jour l'API)           ║
║                                                              ║
║   [0] ❌ Quitter                                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

def scrape_now():
    """Option 1: Scraper maintenant"""
    clear_screen()
    print("\n🔄 SCRAPER MAINTENANT - VERSION OPTIMISÉE v3.0\n")
    print("-" * 40)
    
    print("Mode de scraping:")
    print("[1] CIBLÉ (recommandé) - Recherches multiples variées")
    print("[2] GÉNÉRAL - Recherche unique classique")
    mode_choice = input("\nTon choix [1/2]: ").strip() or "1"
    mode = "targeted" if mode_choice == "1" else "general"
    
    try:
        pages = int(input("\n📄 Pages par recherche [1-20]: ") or "10")
        pages = max(1, min(20, pages))
    except:
        pages = 10
    
    try:
        annonces = int(input("🚗 Max annonces total [50-500]: ") or "200")
        annonces = max(50, min(500, annonces))
    except:
        annonces = 200
    
    print(f"\n✅ Configuration:")
    print(f"   Mode: {mode.upper()}")
    print(f"   Pages/recherche: {pages}")
    print(f"   Max annonces: {annonces}")
    print("\n🚀 Lancement du scraper optimisé...\n")
    
    subprocess.run([sys.executable, "pipeline.py", "--pages", str(pages), "--max", str(annonces), "--mode", mode])
    
    input("\n⏎ Appuie sur Entrée pour continuer...")

def schedule_scraping():
    """Option 2: Programmer le scraping automatique"""
    clear_screen()
    print("\n⏰ PROGRAMMER LE SCRAPING AUTOMATIQUE\n")
    print("-" * 40)
    print("""
Choisis une option:

[1] Tous les jours à 8h00
[2] Tous les jours à 20h00
[3] 2x par jour (8h et 20h)
[4] Personnalisé (choisir l'heure)
[5] Voir les tâches programmées
[6] Supprimer les tâches programmées
[0] Retour
""")
    
    choice = input("Ton choix: ").strip()
    
    if choice == "1":
        create_scheduled_task("08:00")
    elif choice == "2":
        create_scheduled_task("20:00")
    elif choice == "3":
        create_scheduled_task("08:00")
        create_scheduled_task("20:00", "CarAnalytics_Evening")
    elif choice == "4":
        hour = input("Heure (format HH:MM, ex: 14:30): ").strip()
        if hour:
            create_scheduled_task(hour)
    elif choice == "5":
        print("\n📋 Tâches programmées:\n")
        subprocess.run(["schtasks", "/query", "/tn", "CarAnalytics_Scraper"], capture_output=False)
        input("\n⏎ Appuie sur Entrée pour continuer...")
    elif choice == "6":
        subprocess.run(["schtasks", "/delete", "/tn", "CarAnalytics_Scraper", "/f"], capture_output=True)
        subprocess.run(["schtasks", "/delete", "/tn", "CarAnalytics_Evening", "/f"], capture_output=True)
        print("✅ Tâches supprimées!")
        input("\n⏎ Appuie sur Entrée pour continuer...")

def create_scheduled_task(time_str, task_name="CarAnalytics_Scraper"):
    """Créer une tâche planifiée Windows"""
    script_path = Path(__file__).parent / "pipeline.py"
    python_exe = sys.executable
    
    # Créer un batch file pour lancer le scraper
    batch_content = f'''@echo off
cd /d "{Path(__file__).parent}"
"{python_exe}" pipeline.py --pages 3
'''
    batch_path = Path(__file__).parent / "auto_scrape.bat"
    batch_path.write_text(batch_content)
    
    # Créer la tâche planifiée
    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", str(batch_path),
        "/sc", "daily",
        "/st", time_str,
        "/f"  # Force (remplace si existe)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"\n✅ Tâche créée: Scraping tous les jours à {time_str}")
        print(f"   Nom de la tâche: {task_name}")
    else:
        print(f"\n❌ Erreur: {result.stderr}")
    
    input("\n⏎ Appuie sur Entrée pour continuer...")

def show_stats():
    """Option 3: Voir les statistiques"""
    clear_screen()
    print("\n📊 STATISTIQUES DE LA BASE\n")
    print("-" * 40)
    
    import sqlite3
    
    db_path = Path(__file__).parent / "data" / "vehicles.db"
    
    if not db_path.exists():
        print("❌ Base de données non trouvée!")
        input("\n⏎ Appuie sur Entrée pour continuer...")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Total véhicules
    c.execute("SELECT COUNT(*) FROM vehicles")
    total = c.fetchone()[0]
    
    # Prix moyen
    c.execute("SELECT AVG(prix), MIN(prix), MAX(prix) FROM vehicles WHERE prix IS NOT NULL")
    prix = c.fetchone()
    
    # Top marques
    c.execute("""
        SELECT marque, COUNT(*) as cnt 
        FROM vehicles 
        WHERE marque IS NOT NULL 
        GROUP BY marque 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    marques = c.fetchall()
    
    # Top villes
    c.execute("""
        SELECT ville, COUNT(*) as cnt 
        FROM vehicles 
        WHERE ville IS NOT NULL 
        GROUP BY ville 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    villes = c.fetchall()
    
    conn.close()
    
    print(f"""
📈 RÉSUMÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚗 Total véhicules: {total}

💰 Prix:
   • Moyen: {int(prix[0] or 0):,} €
   • Min:   {int(prix[1] or 0):,} €
   • Max:   {int(prix[2] or 0):,} €

🏷️ Top 5 Marques:
""")
    for marque, cnt in marques:
        print(f"   • {marque}: {cnt} véhicules")
    
    print("\n🏙️ Top 5 Villes:")
    for ville, cnt in villes:
        print(f"   • {ville}: {cnt} véhicules")
    
    input("\n⏎ Appuie sur Entrée pour continuer...")

def generate_report():
    """Option 4: Générer le rapport HTML"""
    clear_screen()
    print("\n📄 GÉNÉRATION DU RAPPORT HTML\n")
    print("-" * 40)
    
    subprocess.run([sys.executable, "gen_rapport.py"])
    
    report_path = Path(__file__).parent / "car_analytics_rapport.html"
    if report_path.exists():
        print(f"\n✅ Rapport généré: {report_path}")
        open_file = input("\n🌐 Ouvrir dans le navigateur? [O/n]: ").strip().lower()
        if open_file != 'n':
            os.startfile(str(report_path))
    
    input("\n⏎ Appuie sur Entrée pour continuer...")

def open_api():
    """Option 5: Ouvrir l'API en ligne"""
    import webbrowser
    url = "https://car-analytics-api.onrender.com"
    print(f"\n🌐 Ouverture de {url}...")
    webbrowser.open(url)
    input("\n⏎ Appuie sur Entrée pour continuer...")

def push_to_github():
    """Option 6: Pousser vers GitHub"""
    clear_screen()
    print("\n📤 MISE À JOUR GITHUB & API\n")
    print("-" * 40)
    
    print("📝 Ajout des fichiers modifiés...")
    subprocess.run(["git", "add", "-A"])
    
    message = input("💬 Message du commit (ou Entrée pour auto): ").strip()
    if not message:
        from datetime import datetime
        message = f"Update data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    print(f"\n📦 Commit: {message}")
    subprocess.run(["git", "commit", "-m", message])
    
    print("\n🚀 Push vers GitHub...")
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ GitHub mis à jour!")
        print("⏳ L'API Render va se redéployer automatiquement (2-3 min)")
        print("🌐 https://car-analytics-api.onrender.com")
    else:
        print(f"\n❌ Erreur: {result.stderr}")
    
    input("\n⏎ Appuie sur Entrée pour continuer...")

def main():
    while True:
        print_menu()
        choice = input("👉 Ton choix [0-6]: ").strip()
        
        if choice == "1":
            scrape_now()
        elif choice == "2":
            schedule_scraping()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            generate_report()
        elif choice == "5":
            open_api()
        elif choice == "6":
            push_to_github()
        elif choice == "0":
            clear_screen()
            print("\n👋 À bientôt!\n")
            break
        else:
            print("❌ Choix invalide!")

if __name__ == "__main__":
    main()
