# Souss Agri-Pack — Premier cas pédagogique

**Statut : proposition de conception, à valider ensemble.**

**Décision confirmée :** poursuivre Com-sim / Souss Agri-Pack et lui ajouter une expérience d'apprentissage. Le présent document ne valide ni un calendrier, ni un budget, ni la conformité réglementaire du moteur.

## 1. Objectif proposé

Permettre à un étudiant de relier une vente à crédit, une créance client, un effet de commerce et une entrée de trésorerie, puis d'expliquer le rôle du financement bancaire.

Public proposé : étudiants de fin de cursus en comptabilité/finance préparant un stage. Documents et vocabulaire métier en français ; travail dans Excel, sans application dédiée pour ce premier cas. Ces choix restent à confirmer.

Cette approche reprend la progression comptabilité → analyse → trésorerie du document `Planing-2.docx`, section « Freeze the scope before starting », en l'adaptant à l'entreprise industrielle déjà présente dans Com-sim plutôt qu'en créant un nouveau distributeur.

## 2. Premier cas : « De la facture au crédit bancaire »

**Rôle :** comptable junior au sein de la direction financière de Souss Agri-Pack.

**Situation proposée :** la responsable financière demande de justifier les montants reçus lors des remises à l'escompte et de distinguer ces avances bancaires du règlement des clients à l'échéance.

Le cas ne suppose pas une crise de trésorerie : une telle situation devrait être démontrée par les données ou construite explicitement comme variante pédagogique.

| Étape | Travail demandé | Livrable apprenant | Vérification envisagée |
|---|---|---|---|
| Rapprocher | Relier les factures aux effets et aux pièces comptables correspondantes | Tableau de correspondance avec références, dates et montants | Références traçables et concordance facture TTC / nominal |
| Justifier | Rapprocher nominal, agios et montant net crédité | Tableau de rapprochement et explication des écarts | Calculs en MAD au centime ; toute anomalie doit être justifiée |
| Expliquer | Distinguer vente, mobilisation de créance, crédit bancaire et dénouement à l'échéance | Note courte à la responsable financière | Raisonnement étayé par les pièces ; revue humaine à partir d'une grille |

**Périmètre initial proposé :** sélectionner quelques effets complets parmi les factures de janvier 2025 et suivre leur cycle jusqu'à l'échéance. La sélection finale et les dates d'observation restent à fixer. Il ne s'agit pas de présenter les statuts de fin d'année comme des statuts au 31 janvier.

## 3. Faisabilité observée dans les fichiers existants

Une lecture programmatique, sans modification des données, a constaté sur le jeu re-généré (Septembre 2026) :

- 20 factures datées de janvier 2025 dans `data/fy2025/operational/sales_invoices.csv`, dont 16 avec effet correspondant dans `data/fy2025/operational/commercial_papers.csv` (les 4 restantes sont en virement/chèque/espèces et n'ont pas de traite par conception).
- Pour chacun de ces 16 effets, égalité entre le TTC de la facture et le nominal de l'effet.
- Pour ces effets, égalité entre montant net reçu + agios totaux et nominal, vérifiée avec `Decimal`.
- Une chaîne de pièces consultable dans `data/fy2025/accounting/journal_general.csv` pour le premier exemple : `FAC-2025-00001`, `LCR-2025-00001`, `REM-LCR-2025-00001`, `BDC-LCR-2025-00001`, `ECH-LCR-2025-00001`.

Ces contrôles établissent la faisabilité de rapprochement sur un jeu corrigé et certifié (chronologie d'escompte, modes de règlement, dénouements et statuts vérifiés par la revue documentaire). Ils ne constituent pas un audit complet des doublons, des échéances, des écritures, du calcul des agios ou des règles fiscales au-delà des contrôles exécutés.

## 4. Prototype documentaire et revue complémentaire

Une facture et un avis de crédit liés au cycle `FAC-2025-00072` ont été produits séparément dans `../../document_work/samples/learner/`. Ce cycle d’avril, sélectionné pour sa chronologie cohérente, sert à valider la présentation ; il ne remplace pas encore le périmètre pédagogique proposé pour janvier.

La revue de l’ensemble du jeu avait révélé des anomalies de dates d’escompte, de modes de règlement et d’identifiants d’écriture que les contrôles monétaires ci-dessus ne détectent pas. **Ces défauts ont été corrigés à la source dans le moteur (Septembre 2026), le jeu FY2025 a été re-généré et la revue ne remonte plus aucun constat** (`../../document_work/review/document_readiness.json`, `ready_for_full_learner_distribution: true`). Voir `../../document_work/README_Documents_et_Revue.md` pour la traçabilité correction par correction.

## 5. Dossier pédagogique à préparer après validation du cas

1. **Brief apprenant** : contexte, rôle, objectifs et consignes autonomes.
2. **Pièces de travail** : extraits sélectionnés, références explicites et dates d'observation. Tout avis bancaire reconstitué devra être identifié comme synthétique ; le journal seul n'est pas une preuve bancaire indépendante.
3. **Modèle de réponse** : tableaux de rapprochement et trame de note.
4. **Corrigé formateur séparé** : calculs attendus, pièces justificatives, explications et grille d'évaluation.

Le corrigé ne doit pas être caché dans un onglet du classeur apprenant ni publié dans un dépôt accessible aux participants. Une éventuelle anomalie sera définie et documentée avant d'être introduite dans une copie ; aucun écart existant ne sera présumé volontaire.

## 6. Conditions avant diffusion

- Vérifier les traitements comptables pertinents au regard du référentiel marocain et sourcer les règles fiscales applicables à la période. Un test logiciel réussi n'est pas une validation professionnelle ; conserver `[TO VERIFY]` lorsqu'une règle n'est pas confirmée.
- Contrôler les liens et la chronologie de chaque effet retenu, puis définir les statuts à chaque date d'observation sans utiliser une information future dans une étape antérieure.
- Remplacer les dénominations de contreparties reprenant des marques réelles dans le paquet pédagogique, avec une correspondance formateur privée. Les premiers enregistrements de `sales_invoices.csv` montrent que ce point nécessite une revue.
- Porter la mention « Simulation pédagogique — entreprise fictive — données synthétiques » sur chaque document distribué.
- Vérifier que toutes les réponses attendues sont déductibles des pièces fournies. Accepter des formulations différentes lorsque le raisonnement est correct.
- Prévoir un point de reprise corrigé après la première étape pour qu'une erreur initiale ne bloque pas toute la suite.
- Faire essayer le cas à un premier apprenant, relever les ambiguïtés et corriger le dossier avant d'élargir le test.

Ces conditions reprennent notamment les sections « Keep three separate layers », « Verification checks » et « Week 6 — Run a small observed pilot » de `Planing-2.docx`.

## 7. Limites de cette première étape

Le moteur, les paramètres et les données FY2025 restent inchangés. Pas de deuxième entreprise, de génération FY2026, de plateforme, de notation par IA ou de scénario de financement à embranchements à ce stade.

**Prochain livrable proposé :** un brief apprenant complet pour le premier cas, puis son corrigé vérifié et les pièces nécessaires. La décision sur le public exact et le niveau de difficulté précède la production du paquet.
