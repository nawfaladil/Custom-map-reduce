# MapReduce Personnalisé pour le Word Count

Ce projet implémente une version personnalisée de MapReduce pour compter les mots en utilisant un système distribué. Une machine locale gère la répartition des tâches, le shuffle, et l'agrégation des résultats.

---

## Fonctionnement

1. **Distribution des données** : La machine locale qui à une connexion ssh avec les machines distantes répartit les mots entre elles et leur envoie la liste des participants.
2. **Phase de shuffle** : Les machines échangent les mots selon un critère (longueur modulo nombre de machines).
3. **Comptage** : Chaque machine compte les occurrences des mots qui lui sont attribués.
4. **Agrégation** : Les résultats sont renvoyés à la machine locale, qui regroupe le tout.

---

## Structure du Projet

- **`machines.txt`** : Liste des machines distantes.
- **`input_strings.txt`** : Chaîne de mots à traiter.
- **`deploy_new.sh`** : Script pour déployer le script.py sur la machine distante, il recrée le dossier deploiement depuis le début pour reprendre les étapes.
- **`envoyeur.py`** : Script principal exécuté sur la machine locale.
- **`script.py`** : Script exécuté sur chaque machine distante.

---

## Utilisation

1. Configurez les machines dans `machines.txt` et le texte d’entrée dans `input_strings.txt`.
2. Configurez votre username ainsi qu'un mot de passe si vous n'avez pas votre clé ssh dans les machines distantes, sinon seul l'username suffira.
3. Lancez le script :
   ```bash
   bash deploy_new.sh   
4. Attendre que le serveur soit à l'écoute dans les machines distantes et lancer le script principal envoyeur.py sur votre machine locale.

# Exemple

1. **Entrée (input_strings.txt)** : pomme banane pomme orange banane orange pomme
2. **Sortie (comptage des mots)** : 
pomme : 3
banane : 2
orange : 2

