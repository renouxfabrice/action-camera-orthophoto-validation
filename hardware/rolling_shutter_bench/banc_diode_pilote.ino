/*
  Banc de mesure du temps de lecture — generateur de creneau exact.

  POURQUOI PROGRAMMER LE COMPTEUR PLUTOT QU'APPELER tone() OU analogWrite().
  analogWrite() ne sort que 490 ou 980 Hz sur un Uno, et tone() arrondit sa
  frequence sans le dire : demander 200 Hz y donne 200,32 Hz. Or c'est cette
  frequence qui divise le nombre de bandes pour donner le temps de lecture ;
  une erreur de 0,2 % sur elle se reporte integralement sur le resultat. On
  pilote donc le compteur 16 bits directement, en mode CTC, ce qui donne des
  frequences exactes des lors que la valeur de comparaison tombe juste.

  LA FORMULE.  OCR1A = 16 000 000 / (2 x prediviseur x f) - 1
  Avec le prediviseur 8, ces frequences tombent sans arrondi :
      100 Hz -> 9999      250 Hz -> 3999      833,33 Hz -> 1199
      200 Hz -> 4999      500 Hz -> 1999     1000,00 Hz -> 999

  L'EXACTITUDE RESTE CELLE DU RESONATEUR CERAMIQUE de la carte, environ 0,5 %.
  Elle se reporte telle quelle sur le temps de lecture : on n'annoncera donc
  pas plus de deux chiffres significatifs. C'est la raison pour laquelle le
  protocole prevoit aussi une lampe secteur a 100 Hz exactement, qui sert de
  reference independante.

  COMMANDES, sur le port serie a 115200 bauds :
      f<valeur>   impose une frequence, par exemple  f250
      ?           renvoie la frequence reellement produite
      0           eteint la diode

  La frequence REELLEMENT produite est recalculee depuis la valeur entiere
  chargee dans le registre, et non depuis la consigne : c'est elle qu'il faut
  noter, et elle peut differer de ce qui a ete demande.

  CABLAGE : broche 9 -> resistance 220 ohms -> anode de la diode ; cathode -> GND.
*/

const uint8_t BROCHE = 9;          // OC1A, la seule pilotee par le compteur 1
const uint16_t PREDIVISEUR = 8;
const unsigned long HORLOGE = 16000000UL;

float frequenceReelle = 0.0;

void eteindre() {
  TCCR1A = 0;
  TCCR1B = 0;
  digitalWrite(BROCHE, LOW);
  frequenceReelle = 0.0;
}

// Charge le compteur pour la frequence demandee et renvoie celle qui sortira
// vraiment de la broche, arrondi du registre compris.
float imposer(float demandee) {
  if (demandee < 1.0 || demandee > 20000.0) {
    eteindre();
    return 0.0;
  }
  unsigned long valeur =
      (unsigned long)(HORLOGE / (2.0 * PREDIVISEUR * demandee) + 0.5) - 1UL;
  if (valeur > 65535UL) valeur = 65535UL;

  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  TCCR1A |= (1 << COM1A0);                    // bascule OC1A a chaque egalite
  TCCR1B |= (1 << WGM12) | (1 << CS11);       // CTC, prediviseur 8
  OCR1A = (uint16_t)valeur;
  interrupts();

  return HORLOGE / (2.0 * PREDIVISEUR * (valeur + 1UL));
}

void setup() {
  pinMode(BROCHE, OUTPUT);
  Serial.begin(115200);
  eteindre();
  Serial.println(F("banc diode pret. f<valeur> pour imposer, ? pour relire, 0 pour eteindre."));
}

void loop() {
  if (!Serial.available()) return;
  String ligne = Serial.readStringUntil('\n');
  ligne.trim();
  if (ligne.length() == 0) return;

  if (ligne == "?") {
    Serial.print(F("frequence reelle "));
    Serial.print(frequenceReelle, 4);
    Serial.println(F(" Hz"));
  } else if (ligne == "0") {
    eteindre();
    Serial.println(F("diode eteinte"));
  } else if (ligne.charAt(0) == 'f' || ligne.charAt(0) == 'F') {
    float demandee = ligne.substring(1).toFloat();
    frequenceReelle = imposer(demandee);
    Serial.print(F("demande "));
    Serial.print(demandee, 3);
    Serial.print(F(" Hz -> reelle "));
    Serial.print(frequenceReelle, 4);
    Serial.print(F(" Hz  (OCR1A = "));
    Serial.print(OCR1A);
    Serial.println(F(")"));
  } else {
    Serial.println(F("commande inconnue"));
  }
}
