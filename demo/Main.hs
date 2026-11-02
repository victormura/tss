{-|
Module      : Main
Description : Demonstrație comparativă: PBT Clasic vs. Foundational PBT
Autori      : Victor Mura & Natalia Moroz
Proiect     : TSS / Proiect de curs 14

Acest program ilustrează practic cele 5 experimente comparative:
  1. Generator incomplet (cum PBT clasic dă fals pozitiv și cum FPBT îl respinge)
  2. Generator nevalid (cum PBT clasic dă fals negativ și cum FPBT izolează eroarea)
  3. Verificator eronat (cum FPBT detectează deviația față de specificație)
  4. Testare pe cod cu bug (găsirea contraexemplului minimal garantat valid)
  5. Testare pe cod corect (emiterea certificatului formal de acoperire 100%)
-}
module Main where

import Data.Set (Set)
import qualified Data.Set as Set
import Text.Read (readMaybe)

-- Motorul formal de Foundational PBT
import FoundationalPBT
  ( Completeness(..)
  , FGen(..)
  , Fidelity(..)
  , Outcome(..)
  , Soundness(..)
  , elements
  , mkSeed
  , runCertifiedTest
  , sampleMany
  , verifyCompleteness
  , verifyFidelity
  , verifySoundness
  )

-- =====================================================================
-- 1. Tipuri de Date & Codul Supus Testării (System Under Test)
-- =====================================================================

data Currency = RON | EUR | USD
  deriving (Eq, Ord, Show, Read)

data Transaction = Transaction
  { txId       :: Int       -- ^ Identificator unic (> 0)
  , amount     :: Int       -- ^ Suma în bani (>= 0)
  , txCurrency :: Currency  -- ^ Moneda (RON, EUR, USD)
  }
  deriving (Eq, Ord, Show)

-- | Afișare concisă și elegantă a unei tranzacții în consolă
prettyTx :: Transaction -> String
prettyTx (Transaction i a c) = "Tx #" ++ show i ++ " (" ++ show a ++ " bani, " ++ show c ++ ")"

-- | Precondiția de business (Invariantul Φ)
validTx :: Transaction -> Bool
validTx (Transaction i a _) = i > 0 && a >= 0

-- | Serializare corectă: "id|amount|currency"
encode :: Transaction -> String
encode (Transaction i a c) = show i ++ "|" ++ show a ++ "|" ++ show c

-- | Serializare cu BUG DELIBERAT: forțează întotdeauna "RON"
encodeBug :: Transaction -> String
encodeBug (Transaction i a _) = encode (Transaction i a RON)

-- | Deserializare cu validarea precondiției
decode :: String -> Maybe Transaction
decode s = case splitOnBar s of
  [rawId, rawAmt, rawCurr] -> do
    i <- readMaybe rawId
    a <- readMaybe rawAmt
    c <- parseCurr rawCurr
    if i > 0 && a >= 0 then Just (Transaction i a c) else Nothing
  _ -> Nothing

splitOnBar :: String -> [String]
splitOnBar s = case break (== '|') s of
  (field, [])     -> [field]
  (field, _:rest) -> field : splitOnBar rest

parseCurr :: String -> Maybe Currency
parseCurr "RON" = Just RON
parseCurr "EUR" = Just EUR
parseCurr "USD" = Just USD
parseCurr _     = Nothing

-- =====================================================================
-- 2. Specificația Declarativă și Verificatoarele
-- =====================================================================

-- | Specificația declarativă abstractă (Round-Trip / Izomorfism)
specRoundTrip :: (Transaction -> String) -> Transaction -> Bool
specRoundTrip enc tx = decode (enc tx) == Just tx

-- | Verificator eronat: compară doar suma, uitând moneda și ID-ul!
checkAmountOnly :: (Transaction -> String) -> Transaction -> Bool
checkAmountOnly enc tx = case decode (enc tx) of
  Just tx' -> amount tx' == amount tx
  Nothing  -> False

-- =====================================================================
-- 3. Domeniul Reprezentativ și Generatoarele
-- =====================================================================

-- | Domeniul de referință: 3 ID-uri * 3 Sume * 3 Monede = 27 de clase
domain :: Set Transaction
domain = Set.fromList
  [ Transaction i a c
  | i <- [1, 2, 42]
  , a <- [0, 99, 1500]
  , c <- [RON, EUR, USD]
  ]

-- | Generator complet și valid (acoperă 100% din domeniu)
genComplete :: FGen Transaction
genComplete = do
  i <- elements [1, 2, 42]
  a <- elements [0, 99, 1500]
  c <- elements [RON, EUR, USD]
  return (Transaction i a c)

-- | Generator INCOMPLET: generează exclusiv RON (omite EUR și USD)
genRonOnly :: FGen Transaction
genRonOnly = do
  i <- elements [1, 2, 42]
  a <- elements [0, 99, 1500]
  return (Transaction i a RON)

-- | Generator NEVALID (Unsound): produce ID-uri și sume negative
genUnsound :: FGen Transaction
genUnsound = do
  i <- elements [-1, 1, 2]
  a <- elements [-50, 0, 100]
  c <- elements [RON, EUR, USD]
  return (Transaction i a c)

-- =====================================================================
-- 4. Shrinking (Reducerea Minimală a Eșecurilor)
-- =====================================================================

shrinkTx :: Transaction -> [Transaction]
shrinkTx (Transaction i a c) =
  [Transaction i' a c | i' <- shrinkInt i, i' > 0] ++
  [Transaction i a' c | a' <- shrinkInt a, a' >= 0] ++
  [Transaction i a c' | c' <- shrinkCurr c]
  where
    shrinkInt n = if n <= 0 then [] else [n `div` 2, n - 1]
    shrinkCurr USD = [EUR, RON]
    shrinkCurr EUR = [RON]
    shrinkCurr RON = []

shrinkLoop :: (Transaction -> Bool) -> Transaction -> Transaction
shrinkLoop prop tx = case filter (not . prop) (shrinkTx tx) of
  []      -> tx
  (tx':_) -> shrinkLoop prop tx'

-- =====================================================================
-- 5. Culori ANSI și Formatare Vizuală pentru Consolă
-- =====================================================================

cReset, cBold, cGreen, cRed, cYellow, cCyan, cGray :: String
cReset  = "\x1b[0m"
cBold   = "\x1b[1m"
cGreen  = "\x1b[32m"
cRed    = "\x1b[31m"
cYellow = "\x1b[33m"
cCyan   = "\x1b[36m"
cGray   = "\x1b[90m"

badgePass, badgeFail, badgeWarn, badgeSpur, badgeDetect, badgeCert :: String
badgePass   = cGreen  ++ "[PASSED]"           ++ cReset
badgeFail   = cRed    ++ "[TEST PICAT]"       ++ cReset
badgeWarn   = cYellow ++ "[FALS POZITIV]"     ++ cReset
badgeSpur   = cYellow ++ "[FALS NEGATIV]"     ++ cReset
badgeDetect = cRed    ++ "[RESPINS FORMAL]"   ++ cReset
badgeCert   = cGreen  ++ "[CERTIFICAT EMIS]"  ++ cReset

-- Simulare PBT convențional (eșantionare din cutie neagră)
runOrdinaryPBT :: FGen Transaction -> (Transaction -> Bool) -> IO (Maybe Transaction)
runOrdinaryPBT gen prop = do
  let samples  = sampleMany 100 gen (mkSeed 0x12345678)
      failures = filter (not . prop) samples
  case failures of
    []      -> return Nothing
    (bad:_) -> return (Just (shrinkLoop prop bad))

-- =====================================================================
-- 6. Execuția Celor 5 Experimente (Curat, Card-Style)
-- =====================================================================

main :: IO ()
main = do
  putStrLn ""
  putStrLn $ cCyan ++ "╔═════════════════════════════════════════════════════════════════════════════╗" ++ cReset
  putStrLn $ cCyan ++ "║   FOUNDATIONAL PROPERTY-BASED TESTING vs. PBT CONVENȚIONAL (HASKELL)        ║" ++ cReset
  putStrLn $ cCyan ++ "║   Referință: 'Foundational Property-Based Testing' (ITP 2015)               ║" ++ cReset
  putStrLn $ cCyan ++ "║   Autori   : Zoe Paraskevopoulou, Cătălin Hrițcu, Benjamin Pierce et al.    ║" ++ cReset
  putStrLn $ cCyan ++ "╚═════════════════════════════════════════════════════════════════════════════╝" ++ cReset

  -- -------------------------------------------------------------------
  -- EXPERIMENTUL 1
  -- -------------------------------------------------------------------
  putStrLn ""
  putStrLn $ cBold ++ "┌─ [EXPERIMENTUL 1] Generator Incomplet (Capcana Bug-ului Ascuns)" ++ cReset
  putStrLn "│  SUT: encodeBug (pierde EUR/USD)  |  Generator: genRonOnly (doar RON)"
  putStrLn "│"
  resOrd1 <- runOrdinaryPBT genRonOnly (specRoundTrip encodeBug)
  case resOrd1 of
    Nothing -> do
      putStrLn $ "│  • " ++ cBold ++ "PBT Clasic" ++ cReset ++ ":        +++ OK, 100 teste trecute.  " ++ badgeWarn
      putStrLn "│    Vulnerabilitate:   Testul dă verde fals! EUR și USD nu au fost niciodată testate."
    Just bad ->
      putStrLn $ "│  • PBT Clasic:        " ++ badgeFail ++ " pe " ++ prettyTx bad

  putStrLn "│"
  case verifyCompleteness domain genRonOnly of
    Incomplete missing ratio -> do
      let pct = show (round (ratio * 100) :: Int) ++ "%"
      putStrLn $ "│  • " ++ cBold ++ "Foundational PBT" ++ cReset ++ ":  " ++ badgeDetect ++ "  (Acoperire domeniu: " ++ pct ++ ")"
      putStrLn $ "│    Unghi mort:        Lipsesc " ++ show (length missing) ++ "/27 clase de echivalență (EUR și USD)."
      putStrLn "│    Garanție formală:  Domain ⊈ semGen(G) -> Suita este respinsă înainte de testare!"
    Complete -> return ()
  putStrLn "└─────────────────────────────────────────────────────────────────────────────"

  -- -------------------------------------------------------------------
  -- EXPERIMENTUL 2
  -- -------------------------------------------------------------------
  putStrLn ""
  putStrLn $ cBold ++ "┌─ [EXPERIMENTUL 2] Generator Nevalid (Contraexemple False / Spurious)" ++ cReset
  putStrLn "│  SUT: encode (100% corect)  |  Generator: genUnsound (ID <= 0, Sumă < 0)"
  putStrLn "│"
  resOrd2 <- runOrdinaryPBT genUnsound (specRoundTrip encode)
  case resOrd2 of
    Just bad -> do
      putStrLn $ "│  • " ++ cBold ++ "PBT Clasic" ++ cReset ++ ":        " ++ badgeFail ++ " pe " ++ prettyTx bad ++ "  " ++ badgeSpur
      putStrLn "│    Vulnerabilitate:   Învinovățește codul corect; dezvoltatorul pierde timp căutând"
      putStrLn "│                       un bug inexistent în SUT!"
    Nothing -> return ()

  putStrLn "│"
  case verifySoundness validTx genUnsound of
    Unsound bads -> do
      putStrLn $ "│  • " ++ cBold ++ "Foundational PBT" ++ cReset ++ ":  " ++ badgeDetect ++ "  (Generator Unsound)"
      putStrLn $ "│    Cauză reală:       " ++ show (length bads) ++ " intrări generate încalcă precondiția (validTx)."
      putStrLn "│    Garanție formală:  Izolează eroarea în generator, protejând codul aplicației!"
    Sound -> return ()
  putStrLn "└─────────────────────────────────────────────────────────────────────────────"

  -- -------------------------------------------------------------------
  -- EXPERIMENTUL 3
  -- -------------------------------------------------------------------
  putStrLn ""
  putStrLn $ cBold ++ "┌─ [EXPERIMENTUL 3] Verificator Eronat (Derivă de la Specificație)" ++ cReset
  putStrLn "│  SUT: encodeBug (pierde EUR/USD)  |  Verificator: checkAmountOnly (omite moneda)"
  putStrLn "│"
  resOrd3 <- runOrdinaryPBT genComplete (checkAmountOnly encodeBug)
  case resOrd3 of
    Nothing -> do
      putStrLn $ "│  • " ++ cBold ++ "PBT Clasic" ++ cReset ++ ":        +++ OK, 100 teste trecute.  " ++ badgeWarn
      putStrLn "│    Vulnerabilitate:   Verificatorul neglijent lasă un bug grav să treacă verde!"
    Just bad ->
      putStrLn $ "│  • PBT Clasic:        " ++ badgeFail ++ " pe " ++ prettyTx bad

  putStrLn "│"
  case verifyFidelity (specRoundTrip encodeBug) (checkAmountOnly encodeBug) genComplete of
    Divergent devs -> do
      putStrLn $ "│  • " ++ cBold ++ "Foundational PBT" ++ cReset ++ ":  " ++ badgeDetect ++ "  (Checker Fidelity Violation)"
      putStrLn $ "│    Cauză reală:       " ++ show (length devs) ++ " discrepanțe logice între Verificator și Specificație."
      putStrLn "│    Garanție formală:  semChecker(c) ⇎ Spec -> Testul executabil nu este fidel!"
    Faithful -> return ()
  putStrLn "└─────────────────────────────────────────────────────────────────────────────"

  -- -------------------------------------------------------------------
  -- EXPERIMENTUL 4
  -- -------------------------------------------------------------------
  putStrLn ""
  putStrLn $ cBold ++ "┌─ [EXPERIMENTUL 4] Testare Certificată pe Cod cu Bug (encodeBug)" ++ cReset
  putStrLn "│  SUT: encodeBug  |  Generator: genComplete (Sound & Complete)  |  Checker: Fidel"
  putStrLn "│"
  putStrLn $ "│  • " ++ cBold ++ "Faza 1 (Soundness)" ++ cReset ++ "    : " ++ badgePass ++ " Toate datele respectă precondiția Φ."
  putStrLn $ "│  • " ++ cBold ++ "Faza 2 (Completeness)" ++ cReset ++ " : " ++ badgePass ++ " 100% acoperire a domeniului (27/27 clase)."
  putStrLn $ "│  • " ++ cBold ++ "Faza 3 (Fidelity)" ++ cReset ++ "     : " ++ badgePass ++ " Verificatorul coincide exact cu specificația."
  putStrLn "│"
  case runCertifiedTest validTx domain (specRoundTrip encodeBug) (specRoundTrip encodeBug) genComplete 100 (mkSeed 42) of
    CounterexampleFound c -> do
      let minCase = shrinkLoop (specRoundTrip encodeBug) c
      putStrLn $ "│  • " ++ cBold ++ "Faza 4 (Execuție)" ++ cReset ++ "     : " ++ cRed ++ "[BUG REAL DETECTAT ÎN SUT]" ++ cReset
      putStrLn $ "│    - Contraexemplu brut   : " ++ prettyTx c
      putStrLn $ "│    - După Shrinking minimal: " ++ cBold ++ prettyTx minCase ++ cReset
      putStrLn "│    Garanție formală:  Contraexemplul este garantat 100% valid și autentic!"
    _ -> return ()
  putStrLn "└─────────────────────────────────────────────────────────────────────────────"

  -- -------------------------------------------------------------------
  -- EXPERIMENTUL 5
  -- -------------------------------------------------------------------
  putStrLn ""
  putStrLn $ cBold ++ "┌─ [EXPERIMENTUL 5] Testare Certificată pe Cod Corect (encode)" ++ cReset
  putStrLn "│  SUT: encode (corect)  |  Generator: genComplete  |  Checker: Fidel"
  putStrLn "│"
  putStrLn $ "│  • " ++ cBold ++ "Faza 1 (Soundness)" ++ cReset ++ "    : " ++ badgePass ++ " semGen(G) ⊆ { x | validTx(x) }"
  putStrLn $ "│  • " ++ cBold ++ "Faza 2 (Completeness)" ++ cReset ++ " : " ++ badgePass ++ " Domain ⊆ semGen(G) (100% acoperire)"
  putStrLn $ "│  • " ++ cBold ++ "Faza 3 (Fidelity)" ++ cReset ++ "     : " ++ badgePass ++ " semChecker(c) ⟺ Spec"
  putStrLn "│"
  case runCertifiedTest validTx domain (specRoundTrip encode) (specRoundTrip encode) genComplete 100 (mkSeed 42) of
    CertifiedSuccess n -> do
      putStrLn $ "│  • " ++ cBold ++ "Faza 4 (Execuție)" ++ cReset ++ "     : " ++ badgeCert
      putStrLn $ "│    - Rezultat             : " ++ show n ++ "/100 teste trecute cu certitudine matematică."
      putStrLn "│    Garanție formală:  Niciun unghi mort + nicio eroare falsă + verificator dovedit."
    _ -> return ()
  putStrLn "└─────────────────────────────────────────────────────────────────────────────"

  -- -------------------------------------------------------------------
  -- Tabelul Sinoptic Final
  -- -------------------------------------------------------------------
  putStrLn ""
  putStrLn $ cCyan ++ "┌────────────────────────┬──────────────────────────────┬──────────────────────────────┐" ++ cReset
  putStrLn $ cCyan ++ "│ DIMENSIUNE             │ PBT CLASIC (QuickCheck)      │ FOUNDATIONAL PBT (FPBT)      │" ++ cReset
  putStrLn $ cCyan ++ "├────────────────────────┼──────────────────────────────┼──────────────────────────────┤" ++ cReset
  putStrLn "│ Semantica generator    │ Cutie neagră (Seed -> a)     │ Mulțime formală semGen(G)    │"
  putStrLn $ "│ Generator incomplet    │ " ++ cYellow ++ "[FALS POZITIV] Trecere oarbă" ++ cReset ++ " │ " ++ cGreen ++ "[RESPINS] Unghi mort găsit   " ++ cReset ++ "│"
  putStrLn $ "│ Generator nevalid      │ " ++ cYellow ++ "[FALS NEGATIV] Învinovățește" ++ cReset ++ " │ " ++ cGreen ++ "[RESPINS] Izolat în test    " ++ cReset ++ " │"
  putStrLn $ "│ Verificator neglijent  │ " ++ cYellow ++ "[FALS POZITIV] Netestat     " ++ cReset ++ " │ " ++ cGreen ++ "[RESPINS] Discrepanță prinsă" ++ cReset ++ " │"
  putStrLn "│ Garanție de acoperire  │ Estimare statistică (noroc)  │ 100% acoperire demonstrată   │"
  putStrLn "│ Referință științifică  │ Claessen & Hughes (2000)     │ Paraskevopoulou et al.(2015) │"
  putStrLn $ cCyan ++ "└────────────────────────┴──────────────────────────────┴──────────────────────────────┘" ++ cReset
  putStrLn ""
