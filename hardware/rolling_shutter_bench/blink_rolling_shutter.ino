/*
 * blink_rolling_shutter.ino — banc de mesure du temps de lecture
 * d'un capteur a obturateur deroulant (rolling shutter).
 *
 * LE PRINCIPE
 * -----------
 * Un capteur a obturateur deroulant lit ses lignes l'une apres l'autre. On
 * fait clignoter une LED a intervalle exactement connu et on la
 * photographie : les lignes exposees pendant un allumage sont claires, les
 * autres sombres, et la photo porte des bandes. Chaque bande dure un
 * intervalle de clignotement.
 *
 *     temps de lecture = nombre de bandes x duree d'un etat
 *
 * C'est ce temps que reclame ODM par --rolling-shutter-readout.
 *
 * POURQUOI QUATRE CADENCES, ET POURQUOI ELLES DEFILENT SEULES
 * ------------------------------------------------------------
 * On ne connait pas d'avance le temps de lecture du capteur qu'on mesure :
 * il vaut entre dix et quarante millisecondes selon les modeles. Et l'on ne
 * connait pas davantage la vitesse d'obturation que la camera choisira,
 * puisque aucune GoPro ne permet de la fixer en mode photo.
 *
 * Or les deux se contraignent. Une cadence trop rapide devant l'obturation
 * melange les etats et efface les bandes ; une cadence trop lente n'en donne
 * que trois ou quatre, et l'incertitude explose. La bonne cadence depend
 * donc de deux inconnues.
 *
 * Plutot que de deviner, on les balaie toutes. Quatre cadences couvrent les
 * obturations du 1/250 au 1/8000 de seconde, et l'une au moins donnera une
 * photo exploitable quel que soit le capteur. Il suffira de garder celle-la.
 *
 * ET POURQUOI SANS BOUTON. Sur le terrain — devant un rayon de magasin, par
 * exemple — on ne peut ni rebrancher un ordinateur ni cabler quoi que ce
 * soit. La carte alterne donc seule et ANNONCE la cadence en cours par des
 * eclats longs : un eclat pour la premiere, deux pour la deuxieme, et ainsi
 * de suite. On compte les eclats, on photographie pendant la phase qui
 * suit. Rien a toucher.
 *
 * LE MONTAGE, AU COMPLET
 * ----------------------
 *     broche 9  ---[ resistance 220 ohms ]---|>|--- GND
 *                                          LED
 *                                    (patte longue vers la resistance)
 *
 * Deux fils, une resistance, une LED. Rien d'autre. Une batterie USB ou le
 * coupleur six piles du kit suffisent a l'alimenter loin de tout ordinateur.
 */

// ── les quatre cadences, en microsecondes par ETAT de la LED ────────────
//
// Une bande dure un etat. Pour un capteur dont la lecture vaut 25 ms :
//
//   2000 us -> environ  12 bandes   convient a une obturation lente
//   1000 us -> environ  25 bandes   le cas courant, et la convention d'ODM
//    600 us -> environ  42 bandes
//    250 us -> environ 100 bandes   exige une obturation tres rapide
//
// La cadence retenue sera la plus rapide dont les bandes restent franches :
// l'incertitude decroit avec leur nombre, tant qu'elles se distinguent.
//
// POURQUOI 600 ET NON 500. Ces quatre valeurs ne sont volontairement PAS
// en rapports simples. Avec 2000/1000/500/250 — soit 8:4:2:1 — le rapport
// entre deux nombres de bandes ne designe pas un couple unique : un rapport
// de deux peut venir de 2000/1000, de 1000/500 ou de 500/250. L'analyse ne
// pouvait donc pas retrouver seule la cadence, et il fallait compter les
// eclats a l'oeil.
//
// Avec 2000/1000/600/250, les douze rapports possibles sont TOUS distincts,
// et separes d'au moins dix-huit pour cent — trente fois l'incertitude de
// mesure. Deux photos suffisent alors a lever l'ambiguite, et l'operateur
// n'a plus rien a compter.
const unsigned long CADENCES_US[] = {2000UL, 1000UL, 600UL, 250UL};
const int NOMBRE_CADENCES = 4;
int cadence = 0;

// Duree de chaque phase. Quinze secondes laissent le temps de cadrer et de
// declencher deux ou trois fois sans se presser, et le cycle complet tient
// en une minute et demie — supportable debout dans un magasin.
const unsigned long PHASE_MS = 15000UL;
unsigned long debut_phase = 0;

// Vrai tant que personne ne pilote la carte : elle balaie alors seule. Un
// ordre recu par le port serie la fige sur une cadence, et 'a' la relache.
bool balayage = true;

const unsigned long HORLOGE_HZ = 16000000UL;   // quartz de la UNO
const unsigned int DIVISEUR = 8;               // pas de comptage : 0,5 us
const int BROCHE_LED = 9;                      // OC1A — ne pas changer

void appliquer_cadence() {
  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  TCCR1A |= (1 << COM1A0);   // bascule OC1A a chaque egalite — en materiel
  TCCR1B |= (1 << WGM12);    // mode CTC : le compteur repart de zero
  TCCR1B |= (1 << CS11);     // diviseur par huit

  //   pas = duree_us x (horloge / diviseur) / 1 000 000
  // On retranche un parce que le compteur part de zero.
  unsigned long pas =
      (CADENCES_US[cadence] * (HORLOGE_HZ / DIVISEUR)) / 1000000UL;
  OCR1A = (unsigned int)(pas - 1);
  interrupts();
}

void annoncer_par_la_led(int nombre) {
  // LE SEUL MOYEN DE SAVOIR OU L'ON EN EST. Meme la plus lente des quatre
  // cadences bat deux cent cinquante fois par seconde : l'oeil ne distingue
  // rien, et les quatre se ressemblent exactement — la LED parait allumee en
  // continu dans tous les cas. Sans ce signal, on photographierait sans
  // savoir a quoi comparer, et une mesure dont on ignore la cadence n'est
  // pas une mesure.
  //
  // On retire le controle du timer sur la broche pour la piloter a la main ;
  // sans cela, digitalWrite resterait sans effet.
  TCCR1A &= ~(1 << COM1A0);
  pinMode(BROCHE_LED, OUTPUT);
  digitalWrite(BROCHE_LED, LOW);
  delay(900);                       // noir franc : le signal commence ici
  for (int i = 0; i < nombre; i++) {
    digitalWrite(BROCHE_LED, HIGH);
    delay(450);                     // eclat long, impossible a confondre
    delay(0);
    digitalWrite(BROCHE_LED, LOW);
    delay(300);
  }
  delay(600);
  appliquer_cadence();              // retour au regime de mesure
}

void annoncer_au_port() {
  Serial.println();
  Serial.print(F("=== cadence "));
  Serial.print(cadence + 1);
  Serial.print(F(" sur "));
  Serial.print(NOMBRE_CADENCES);
  Serial.print(F(" : "));
  Serial.print(CADENCES_US[cadence] / 1000.0, 3);
  Serial.println(F(" ms par etat ==="));
  Serial.print(F("  signal carre a "));
  Serial.print(1000000.0 / (2.0 * CADENCES_US[cadence]), 1);
  Serial.print(F(" Hz, OCR1A = "));
  Serial.print(OCR1A);
  Serial.print(F(", erreur d'arrondi "));
  Serial.print(100.0 * (((OCR1A + 1.0) * 1000000.0
                         / (HORLOGE_HZ / DIVISEUR)) - CADENCES_US[cadence])
               / CADENCES_US[cadence], 4);
  Serial.println(F(" %"));
  Serial.print(F("  obturation minimale utile : plus rapide que 1/"));
  Serial.println((int)(1000000.0 / CADENCES_US[cadence]));
  Serial.print(F("  dans l'appli : choisir "));
  Serial.print(CADENCES_US[cadence] / 1000.0, 3);
  Serial.println(F(" ms"));
}

void passer_a_la_phase_suivante() {
  appliquer_cadence();
  annoncer_par_la_led(cadence + 1);
  annoncer_au_port();
  debut_phase = millis();
}

void setup() {
  pinMode(BROCHE_LED, OUTPUT);
  Serial.begin(115200);
  delay(200);
  Serial.println(F("--- banc de mesure du temps de lecture ---"));
  Serial.println(F("Quatre cadences defilent seules, 15 s chacune."));
  Serial.println(F("La LED les annonce par des ECLATS LONGS :"));
  Serial.println(F("  1 eclat  -> 2,000 ms par etat"));
  Serial.println(F("  2 eclats -> 1,000 ms"));
  Serial.println(F("  3 eclats -> 0,600 ms"));
  Serial.println(F("  4 eclats -> 0,250 ms"));
  Serial.println(F("Les eclats ne servent qu'a se reperer : les cadences"));
  Serial.println(F("ne sont pas en rapports simples, et l'appli les"));
  Serial.println(F("identifie seule des qu'on lui donne deux photos."));
  Serial.println();
  Serial.println(F("Ordres acceptes : '1'..'4' fige une cadence,"));
  Serial.println(F("'a' rend le balayage autonome, '?' fait le point."));

  cadence = 0;
  passer_a_la_phase_suivante();
}

void traiter_ordre(char ordre) {
  // '1' a '4' : fige la cadence correspondante.
  // 'a'       : rend la carte a son balayage autonome.
  // '?'       : redit ou l'on en est.
  if (ordre >= '1' && ordre <= '0' + NOMBRE_CADENCES) {
    balayage = false;
    cadence = ordre - '1';
    appliquer_cadence();
    // Pas d'eclats ici : le pilote connait deja la cadence, et les eclats
    // gacheraient une photo prise juste apres l'ordre.
    annoncer_au_port();
    Serial.println(F("  (mode pilote : balayage suspendu)"));
  } else if (ordre == 'a' || ordre == 'A') {
    balayage = true;
    debut_phase = millis();
    Serial.println(F("  (balayage autonome repris)"));
  } else if (ordre == '?') {
    annoncer_au_port();
    Serial.print(F("  mode : "));
    Serial.println(balayage ? F("balayage autonome") : F("pilote"));
  }
}

void loop() {
  // Le clignotement de mesure ne passe pas par ici : le timer s'en charge
  // seul, et le rythme de cette boucle n'a aucune influence sur la cadence.
  while (Serial.available() > 0) {
    traiter_ordre((char)Serial.read());
  }
  if (balayage && millis() - debut_phase >= PHASE_MS) {
    cadence = (cadence + 1) % NOMBRE_CADENCES;
    passer_a_la_phase_suivante();
  }
}
