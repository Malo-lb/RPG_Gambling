import json
import os
import random
import time

# =====================================================================
# CONFIGURATION & GESTION DES FICHIERS (MODE SÉCURISÉ)
# =====================================================================
DOSSIER_TEST = "./dossier_danger_test"
FICHIER_SAUVEGARDE = "./sauvegarde_blackjack.json"


class DossierManager:

  def __init__(self, chemin):
    self.chemin = chemin
    self.initialiser_dossier()

  def initialiser_dossier(self):
    if not os.path.exists(self.chemin):
      os.makedirs(self.chemin)
    if len(os.listdir(self.chemin)) == 0:
      self.generer_fichiers(10)

  def generer_fichiers(self, nb):
    if not os.path.exists(self.chemin):
      os.makedirs(self.chemin)
    existant = len(os.listdir(self.chemin))
    for i in range(nb):
      nom = f"donnee_factice_{existant + i + 1}.txt"
      with open(os.path.join(self.chemin, nom), "w") as f:
        f.write(
            "Fichier de test inoffensif pour le Blackjack Danger."
            " [SÉCURISÉ]"
        )

  def compter_fichiers(self):
    return len(os.listdir(self.chemin))

  def lister_fichiers(self):
    return os.listdir(self.chemin)

  def detruire_fichiers(self, mise):
    fichiers = self.lister_fichiers()
    if not fichiers:
      return []
    echantillon = random.sample(fichiers, min(mise, len(fichiers)))
    supprimes = []
    for f in echantillon:
      chemin_complet = os.path.join(self.chemin, f)
      try:
        os.remove(chemin_complet)
        supprimes.append(f)
      except Exception:
        pass
    return supprimes


# =====================================================================
# CLASSES DU JEU DE CARTES (BLACKJACK)
# =====================================================================
VALEURS_CARTES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11,
}
ENSEIGNES = ["♠", "♥", "♦", "♣"]


class Carte:

  def __init__(self, nom, enseigne):
    self.nom = nom
    self.enseigne = enseigne
    self.valeur = VALEURS_CARTES[nom]

  def __str__(self):
    return f"[{self.nom}{self.enseigne}]"


class Paquet:

  def __init__(self):
    self.cartes = []
    self.reinitialiser()

  def reinitialiser(self):
    self.cartes = [
        Carte(nom, enseigne) for nom in VALEURS_CARTES for enseigne in ENSEIGNES
    ]
    random.shuffle(self.cartes)

  def piocher(self):
    if len(self.cartes) == 0:
      self.reinitialiser()
    return self.cartes.pop()

  def voir_prochaine(self):
    if len(self.cartes) == 0:
      self.reinitialiser()
    return self.cartes[-1]


# =====================================================================
# GESTION DU JOUEUR, XP ET SAUVEGARDE
# =====================================================================
class Joueur:

  def __init__(self):
    self.inventaire_powerups = []
    self.niveau = 1
    self.xp = 0
    self.xp_requis = 100
    self.titre = "Novice du Sablier"
    self.stats = {
        "parties_jouees": 0,
        "victoires": 0,
        "defaites": 0,
        "egalites": 0,
        "fichiers_gagnes": 0,
        "fichiers_perdus": 0,
    }
    self.charger_donnees()

  def ajouter_xp(self, montant):
    self.xp += montant
    print(f"✨ (+{montant} XP)")
    while self.xp >= self.xp_requis:
      self.xp -= self.xp_requis
      self.niveau += 1
      self.xp_requis = int(self.xp_requis * 1.5)
      self.mettre_a_jour_titre()
      print(
          f"\n🎉 NIVEAU SUPÉRIEUR ! Vous passez au Niveau {self.niveau} !"
          f" (Titre : {self.titre})"
      )
    self.sauvegarder_donnees()

  def mettre_a_jour_titre(self):
    if self.niveau >= 10:
      self.titre = "Seigneur du Chaos"
    elif self.niveau >= 7:
      self.titre = "Maître du Bac à Sable"
    elif self.niveau >= 4:
      self.titre = "Joueur de l'Ombre"
    elif self.niveau >= 2:
      self.titre = "Aventurier Prudent"
    else:
      self.titre = "Novice du Sablier"

  def ajouter_powerup(self, powerup):
    self.inventaire_powerups.append(powerup)
    self.sauvegarder_donnees()

  def possede_powerup(self, powerup):
    return powerup in self.inventaire_powerups

  def utiliser_powerup(self, powerup):
    if self.possede_powerup(powerup):
      self.inventaire_powerups.remove(powerup)
      self.sauvegarder_donnees()
      return True
    return False

  def afficher_inventaire(self):
    if not self.inventaire_powerups:
      print("🎒 Inventaire : Vide")
    else:
      print(f"🎒 Inventaire : {', '.join(self.inventaire_powerups)}")

  def sauvegarder_donnees(self):
    data = {
        "niveau": self.niveau,
        "xp": self.xp,
        "xp_requis": self.xp_requis,
        "titre": self.titre,
        "inventaire": self.inventaire_powerups,
        "stats": self.stats,
    }
    try:
      with open(FICHIER_SAUVEGARDE, "w") as f:
        json.dump(data, f)
    except Exception:
      pass

  def charger_donnees(self):
    if os.path.exists(FICHIER_SAUVEGARDE):
      try:
        with open(FICHIER_SAUVEGARDE, "r") as f:
          data = json.load(f)
          self.niveau = data.get("niveau", 1)
          self.xp = data.get("xp", 0)
          self.xp_requis = data.get("xp_requis", 100)
          self.titre = data.get("titre", "Novice du Sablier")
          self.inventaire_powerups = data.get("inventaire", [])
          self.stats = data.get("stats", self.stats)
      except Exception:
        pass


# =====================================================================
# MOTEUR PRINCIPAL DU JEU & ÉVÉNEMENTS
# =====================================================================
class JeuBlackjackDanger:

  def __init__(self):
    self.dossier = DossierManager(DOSSIER_TEST)
    self.joueur = Joueur()
    self.paquet = Paquet()

  def afficher_banniere(self):
    print("\n" + "=" * 65)
    print(" 🃏 BLACKJACK DANGER : EDITION LÉGENDAIRE (MODE SÉCURISÉ) 🃏 ")
    print("=" * 65)
    print(
        f"👤 Profil : {self.joueur.titre} (Niveau {self.joueur.niveau} | XP:"
        f" {self.joueur.xp}/{self.joueur.xp_requis})"
    )
    print(
        f"📦 Fichiers dans le bac à sable : {self.dossier.compter_fichiers()}"
    )
    self.joueur.afficher_inventaire()
    print("-" * 65)

  def calculer_score(self, main):
    score = sum(c.valeur for c in main)
    as_count = sum(1 for c in main if c.nom == "A")
    while score > 21 and as_count > 0:
      score -= 10
      as_count -= 1
    return score

  def afficher_main(self, nom, main, masquer_seconde=False):
    if masquer_seconde:
      print(f"{nom} : [{main[0].nom}{main[0].enseigne}] [ ? ] (Score : ?)")
    else:
      cartes_str = " ".join([str(c) for c in main])
      print(f"{nom} : {cartes_str} (Score : {self.calculer_score(main)})")

  def declencher_evenement_aleatoire(self):
    evenements = [
        (
            "Aucun",
            "La table est calme, une manche classique se prépare.",
            1.0,
            1.0,
        ),
        (
            "⚡ Vent de Panique",
            "La tension monte ! Les gains et les pertes sont doublés !",
            2.0,
            2.0,
        ),
        (
            "🍀 Bénédiction des As",
            "La chance sourit : vos As valent toujours 11 sans jamais"
            " dépasser 21 !",
            1.0,
            1.5,
        ),
        (
            "🌑 Éclipse de la Banque",
            "La Banque est désorientée : elle s'arrête à 14 au lieu de 17.",
            1.0,
            1.2,
        ),
    ]
    # Choix pondéré
    choix = random.choices(
        evenements, weights=[50, 20, 15, 15], k=1
    )[0]
    nom_ev, desc_ev, mult_ressource, mult_xp = choix
    print(f"\n⚡ ÉVÉNEMENT DE TABLE : {nom_ev}")
    print(f"👉 {desc_ev}")
    return nom_ev, mult_ressource, mult_xp

  def phase_boutique(self):
    while True:
      print("\n--- 🏪 BOUTIQUE NOIRE ---")
      print("1. Acheter [🛡️ Bouclier] (Coût : 3 fichiers)")
      print("2. Acheter [🔮 Vision] (Coût : 2 fichiers)")
      print("3. Acheter [⚡ Boost Multiplicateur] (Coût : 4 fichiers)")
      print("4. Acheter [❄️ Gel Banque] (Coût : 3 fichiers)")
      print("5. Acheter [🔄 Échange de carte] (Coût : 2 fichiers)")
      print("6. Quitter la boutique")

      choix = input("Votre choix (1-6) : ").strip()
      if choix == "6":
        break

      catalogue = {
          "1": ("🛡️ Bouclier", 3),
          "2": ("🔮 Vision", 2),
          "3": ("⚡ Boost Multiplicateur", 4),
          "4": ("❄️ Gel Banque", 3),
          "5": ("🔄 Échange de carte", 2),
      }

      if choix in catalogue:
        nom_p, cout = catalogue[choix]
        if self.dossier.compter_fichiers() >= cout:
          suppr = self.dossier.detruire_fichiers(cout)
          self.joueur.ajouter_powerup(nom_p)
          print(f"✅ Achat réussi : [{nom_p}] acquis !")
        else:
          print("❌ Pas assez de fichiers dans le dossier !")
      else:
        print("Choix invalide.")

  def mode_quitte_ou_double(self, gains_actuels):
    print("\n🎲 --- MODE QUITTE OU DOUBLE ---")
    print(
        f"Voulez-vous risquer vos {gains_actuels} nouveaux fichiers sur un pile"
        " ou face ?"
    )
    rep = input("Tenter le Quitte ou Double ? (o/n) : ").strip().lower()
    if rep != "o":
      return gains_actuels

    cote = random.choice(["pile", "face"])
    annonce = (
        input("Votre choix ([p]ile / [f]ace) : ").strip().lower()
    )
    choix_joueur = "pile" if annonce.startswith("p") else "face"

    print(f"La pièce tourne... et tombe sur : {cote.upper()} !")
    if choix_joueur == cote:
      nouveaux_gains = gains_actuels * 2
      print(
          f"🎉 INCROYABLE ! C'est gagné ! Vos gains passent de {gains_actuels}"
          f" à {nouveaux_gains} fichiers !"
      )
      return nouveaux_gains
    else:
      print("💥 PERDU ! Le quitte ou double a échoué, les gains s'envolent.")
      return 0

  def executer_tour(self):
    self.joueur.stats["parties_jouees"] += 1
    nb_fichiers = self.dossier.compter_fichiers()

    if nb_fichiers == 0:
      print("\n💀 TOUTES VOS DONNÉES DE TEST ONT ÉTÉ EFFACÉES !")
      rep = (
          input("Régénérer 10 fichiers de test pour reprendre ? (o/n) : ")
          .strip()
          .lower()
      )
      if rep == "o":
        self.dossier.generer_fichiers(10)
        nb_fichiers = self.dossier.compter_fichiers()
      else:
        return False

    self.afficher_banniere()

    action_menu = (
        input(
            "Voulez-vous [J]ouer une main ou accéder à la [B]outique ? "
            "(j/b) : "
        )
        .strip()
        .lower()
    )
    if action_menu == "b":
      self.phase_boutique()
      return True

    # 1. Mise
    while True:
      try:
        mise = int(
            input(
                f"Combien de fichiers voulez-vous miser (1 à {nb_fichiers}) ? "
            )
        )
        if 1 <= mise <= nb_fichiers:
          break
        print(f"Entrez un nombre entre 1 et {nb_fichiers}.")
      except ValueError:
        print("Entrée invalide.")

    # Événement aléatoire de table
    nom_ev, mult_ress, mult_xp = self.declencher_evenement_aleatoire()

    # Boost Multiplicateur
    boost_actif = False
    if self.joueur.possede_powerup("⚡ Boost Multiplicateur"):
      rep = (
          input("Activer [⚡ Boost Multiplicateur] (Gains x3) ? (o/n) : ")
          .strip()
          .lower()
      )
      if rep == "o":
        self.joueur.utiliser_powerup("⚡ Boost Multiplicateur")
        boost_actif = True

    # Distribution
    main_joueur = [self.paquet.piocher(), self.paquet.piocher()]
    main_banque = [self.paquet.piocher(), self.paquet.piocher()]
    banque_gelee = False

    print("\n--- DISTRIBUTION ---")
    self.afficher_main("Joueur", main_joueur)
    self.afficher_main("Banque", main_banque, masquer_seconde=True)

    # 2. Tour du Joueur
    tour_en_cours = True
    while tour_en_cours:
      score_j = (
          sum(c.valeur for c in main_joueur)
          if nom_ev != "🍀 Bénédiction des As"
          else sum(c.valeur if c.nom != "A" else 11 for c in main_joueur)
      )

      # Gestion normale ou bénédiction
      if nom_ev != "🍀 Bénédiction des As":
        score_j = self.calculer_score(main_joueur)

      if score_j >= 21:
        if score_j > 21:
          print("💥 BUST ! Vous avez dépassé 21 !")
        tour_en_cours = False
        break

      if self.joueur.possede_powerup("🔮 Vision"):
        print(f"🔮 [Vision] Prochaine carte : {self.paquet.voir_prochaine()}")

      print("\nActions : [T]irer | [R]ester")
      if self.joueur.possede_powerup("🔄 Échange de carte"):
        print("          [E]changer dernière carte")
      if self.joueur.possede_powerup("❄️ Gel Banque"):
        print("          [G]eler la Banque")

      choix = input("Votre action : ").strip().lower()

      if choix == "t":
        main_joueur.append(self.paquet.piocher())
        self.afficher_main("Joueur", main_joueur)
      elif choix == "r":
        tour_en_cours = False
      elif choix == "e" and self.joueur.utiliser_powerup("🔄 Échange de carte"):
        jetee = main_joueur.pop()
        remplacement = self.paquet.piocher()
        main_joueur.append(remplacement)
        print(f"🔄 {jetee} remplacée par {remplacement} !")
        self.afficher_main("Joueur", main_joueur)
      elif choix == "g" and self.joueur.utiliser_powerup("❄️ Gel Banque"):
        banque_gelee = True
        print("❄️ La Banque est gelée !")

    score_j = (
        self.calculer_score(main_joueur)
        if nom_ev != "🍀 Bénédiction des As"
        else sum(c.valeur if c.nom != "A" else 11 for c in main_joueur)
    )

    # 3. Tour de la Banque
    if score_j <= 21:
      print("\n--- TOUR DE LA BANQUE ---")
      self.afficher_main("Banque", main_banque)
      limite_banque = 14 if nom_ev == "🌑 Éclipse de la Banque" else 17

      if banque_gelee:
        print("❄️ Banque gelée : Fin de tour.")
      else:
        while self.calculer_score(main_banque) < limite_banque:
          print("La Banque pioche...")
          time.sleep(0.4)
          main_banque.append(self.paquet.piocher())
          self.afficher_main("Banque", main_banque)

    score_b = self.calculer_score(main_banque)

    # 4. Résolution
    print("\n" + "=" * 20 + " RÉSULTAT " + "=" * 20)
    victoire, egalite = False, False

    if score_j > 21 and nom_ev != "🍀 Bénédiction des As":
      victoire = False
    elif score_b > 21:
      print("🎉 La Banque explose ! Vous gagnez !")
      victoire = True
    elif score_j > score_b:
      print(f"🎉 Victoire ({score_j} contre {score_b}) !")
      victoire = True
    elif score_j < score_b:
      print(f"❌ Défaite ({score_b} contre {score_j}) !")
      victoire = False
    else:
      print(f"🤝 Égalité parfaite à {score_j} !")
      egalite = True

    # 5. Conséquences
    if victoire:
      self.joueur.stats["victoires"] += 1
      mult = 3 if boost_actif else 2
      gains_bruts = int(mise * mult * mult_ress)

      # Tenter option Quitte ou Double si assez audacieux
      gains_finaux = self.mode_quitte_ou_double(gains_bruts)

      if gains_finaux > 0:
        self.dossier.generer_fichiers(gains_finaux)
        self.joueur.stats["fichiers_gagnes"] += gains_finaux

      # Récompense Power-up
      bonus_possibles = [
          "🛡️ Bouclier",
          "🔮 Vision",
          "⚡ Boost Multiplicateur",
          "❄️ Gel Banque",
          "🔄 Échange de carte",
      ]
      obtenu = random.choice(bonus_possibles)
      self.joueur.ajouter_powerup(obtenu)
      print(f"🎁 BONUS : Power-up [{obtenu}] obtenu !")

      self.joueur.ajouter_xp(int(50 * mult_xp))

    elif egalite:
      self.joueur.stats["egalites"] += 1
      print("🤝 Fichiers récupérés intacts.")
      self.joueur.ajouter_xp(20)

    else:
      self.joueur.stats["defaites"] += 1
      if self.joueur.utiliser_powerup("🛡️ Bouclier"):
        print(
            "\n🛡️ Le Bouclier s'est activé ! Vos fichiers sont sauvés in"
            " extremis."
        )
      else:
        supprimes = self.dossier.detruire_fichiers(mise)
        self.joueur.stats["fichiers_perdus"] += len(supprimes)
        print(f"\n💥 PUNITION : La Banque a détruit {len(supprimes)} fichier(s) :")
        for f in supprimes:
          print(f"  - ❌ {f}")

      self.joueur.ajouter_xp(10)

    return True

  def lancer(self):
    while True:
      if not self.executer_tour():
        break
      continuer = input("\nLancer une autre main ? (o/n) : ").strip().lower()
      if continuer != "o":
        print("\n--- RAPPORT LÉGENDAIRE DE FIN ---")
        print(f"Titre atteint : {self.joueur.titre} (Niveau {self.joueur.niveau})")
        print(f"Parties jouées : {self.joueur.stats['parties_jouees']}")
        print(
            "Victoires / Défaites :"
            f" {self.joueur.stats['victoires']} /"
            f" {self.joueur.stats['defaites']}"
        )
        print(f"Fichiers gagnés : {self.joueur.stats['fichiers_gagnes']}")
        print(f"Fichiers perdus : {self.joueur.stats['fichiers_perdus']}")
        print("Merci d'avoir joué au Blackjack Danger Légendaire !")
        break


if __name__ == "__main__":
  jeu = JeuBlackjackDanger()
  jeu.lancer()