{-|
Module      : Main (QuickCheckOfficial)
Description : Demonstrație folosind biblioteca oficială Test.QuickCheck de pe Hackage
Autori      : Victor Mura & Natalia Moroz
Proiect     : TSS / Proiect de curs 14

Acest fișier folosește biblioteca oficială «Test.QuickCheck» (clasica «cutie neagră»)
pentru a arăta cum se comportă PBT tradițional pe aceleași scenarii din proiect:
  1. Test valid pe cod corect (QuickCheck raportează succes)
  2. Generator incomplet (QuickCheck dă FALS POZITIV: trece testul pe cod cu bug!)
  3. Generator nevalid (QuickCheck dă FALS NEGATIV: dă vina pe cod corect!)
  4. Detecția unui bug real și shrinking nativ QuickCheck
-}
module Main where

import Text.Read (readMaybe)
import Test.QuickCheck
  ( Arbitrary(..)
  , Args(..)
  , Gen
  , Property
  , Result(..)
  , counterexample
  , elements
  , forAll
  , quickCheckWithResult
  , stdArgs
  )

-- =====================================================================
-- 1. Modelul de Date & Logica de Business
-- =====================================================================

data Currency = RON | EUR | USD
  deriving (Eq, Ord, Show, Read)

data Transaction = Transaction
  { txId       :: Int       -- ^ Identificator unic (> 0)
  , amount     :: Int       -- ^ Suma în bani (>= 0)
  , txCurrency :: Currency  -- ^ Moneda tranzacției
  }
  deriving (Eq, Ord, Show)

prettyTx :: Transaction -> String
prettyTx (Transaction i a c) = "Tx #" ++ show i ++ " (" ++ show a ++ " bani, " ++ show c ++ ")"

-- Serializare corectă: "id|amount|currency"
encode :: Transaction -> String
encode (Transaction i a c) = show i ++ "|" ++ show a ++ "|" ++ show c

-- Serializare cu bug deliberat: forțează întotdeauna RON!
encodeBug :: Transaction -> String
encodeBug (Transaction i a _) = encode (Transaction i a RON)

-- Deserializare cu validarea invariantului de business
decode :: String -> Maybe Transaction
decode s = case splitOnBar s of
  [rawId, rawAmt, rawCurr] -> do
    i <- readMaybe rawId
    a <- readMaybe rawAmt
    c <- parseCurr rawCurr
    if i > 0 && a >= 0 then Just (Transaction i a c) else Nothing
  _ -> Nothing
  where
    splitOnBar str = case break (== '|') str of
      (field, [])     -> [field]
      (field, _:rest) -> field : splitOnBar rest

    parseCurr "RON" = Just RON
    parseCurr "EUR" = Just EUR
    parseCurr "USD" = Just USD
    parseCurr _     = Nothing

-- Proprietatea abstractă de Round-Trip (Izomorfism)
propRoundTrip :: (Transaction -> String) -> Transaction -> Property
propRoundTrip enc tx =
  counterexample ("Eșec la deserializare pentru: " ++ prettyTx tx)
    (decode (enc tx) == Just tx)

-- =====================================================================
-- 2. Instanțe Arbitrary Oficiale (QuickCheck)
-- =====================================================================

-- QuickCheck folosește clasa de tipuri 'Arbitrary' pentru a genera date
instance Arbitrary Currency where
  arbitrary = elements [RON, EUR, USD]
  shrink USD = [EUR, RON]
  shrink EUR = [RON]
  shrink RON = []

instance Arbitrary Transaction where
  arbitrary = do
    i <- elements [1, 2, 42, 100]
    a <- elements [0, 99, 1500, 50000]
    c <- arbitrary
    return (Transaction i a c)

  -- Shrinking nativ QuickCheck: simplifică ID-ul, suma și moneda
  shrink (Transaction i a c) =
    [Transaction i' a c | i' <- shrinkInt i, i' > 0] ++
    [Transaction i a' c | a' <- shrinkInt a, a' >= 0] ++
    [Transaction i a c' | c' <- shrink c]
    where
      shrinkInt n = if n <= 0 then [] else [n `div` 2, n - 1]

-- =====================================================================
-- 3. Generatoare Personalizate (Cutii Negre)
-- =====================================================================

-- | Generator INCOMPLET: generează doar RON (omite EUR și USD)
genRonOnly :: Gen Transaction
genRonOnly = do
  i <- elements [1, 2, 42]
  a <- elements [0, 99, 1500]
  return (Transaction i a RON)

-- | Generator NEVALID (Unsound): produce tranzacții cu date negative
genUnsound :: Gen Transaction
genUnsound = do
  i <- elements [-10, -1, 1, 2]
  a <- elements [-500, -1, 0, 100]
  c <- arbitrary
  return (Transaction i a c)

-- =====================================================================
-- 4. Culori ANSI & Formatare
-- =====================================================================

cReset, cBold, cGreen, cRed, cYellow, cCyan, cGray :: String
cReset  = "\x1b[0m"
cBold   = "\x1b[1m"
cGreen  = "\x1b[32m"
cRed    = "\x1b[31m"
cYellow = "\x1b[33m"
cCyan   = "\x1b[36m"
cGray   = "\x1b[90m"

badgePass, badgeFail, badgeWarn :: String
badgePass = cGreen  ++ "[PASSED]"       ++ cReset
badgeFail = cRed    ++ "[TEST PICAT]"   ++ cReset
badgeWarn = cYellow ++ "[FALS POZITIV]" ++ cReset

qcArgs :: Args
qcArgs = stdArgs { maxSuccess = 100, chatty = False }

-- =====================================================================
-- 5. Execuția Testelor cu Test.QuickCheck
-- =====================================================================

main :: IO ()
main = do
  putStrLn ""
  putStrLn $ cCyan ++ "╔═════════════════════════════════════════════════════════════════════════════╗" ++ cReset
  putStrLn $ cCyan ++ "║       TESTARE CU BIBLIOTECA OFICIALĂ: Test.QuickCheck (HACKAGE)             ║" ++ cReset
  putStrLn $ cCyan ++ "║       PBT Tradițional ca o «Cutie Neagră» (Opaque Random Testing)           ║" ++ cReset
  putStrLn $ cCyan ++ "╚═════════════════════════════════════════════════════════════════════════════╝" ++ cReset
  putStrLn ""

  -- -------------------------------------------------------------------
  -- TEST 1: Test valid pe cod corect
  -- -------------------------------------------------------------------
  putStrLn $ cBold ++ "┌── TEST 1: Cod Corect + Generator Complet (Arbitrary) ───────────────────────" ++ cReset
  putStrLn $ "│ SUT        : encode / decode (fără bug-uri)"
  putStrLn $ "│ Generator  : arbitrary :: Gen Transaction (RON, EUR, USD)"
  putStrLn $ "│ Execuție   : QuickCheck rulează 100 de teste aleatoare..."
  res1 <- quickCheckWithResult qcArgs (propRoundTrip encode)
  case res1 of
    Success { numTests = n } -> do
      putStrLn $ "│ Rezultat   : " ++ badgePass ++ " +++ OK, trecut " ++ show n ++ " teste."
      putStrLn $ "│ Concluzie  : " ++ cGreen ++ "Proprietatea de round-trip este validată cu succes." ++ cReset
    _ -> putStrLn "│ Rezultat neașteptat."
  putStrLn $ "└" ++ replicate 75 '─' ++ "\n"

  -- -------------------------------------------------------------------
  -- TEST 2: Limita Cutiei Negre - Generator Incomplet (Fals Pozitiv)
  -- -------------------------------------------------------------------
  putStrLn $ cBold ++ "┌── TEST 2: LIMITA CUTIEI NEGRE: Generator Incomplet (Fals Pozitiv) ─────────" ++ cReset
  putStrLn $ "│ SUT        : encodeBug (ignoră EUR/USD, salvează forțat RON!)"
  putStrLn $ "│ Generator  : genRonOnly (produce doar RON din greșeală)"
  putStrLn $ "│ Execuție   : QuickCheck testează 'forAll genRonOnly'..."
  res2 <- quickCheckWithResult qcArgs (forAll genRonOnly (propRoundTrip encodeBug))
  case res2 of
    Success { numTests = n } -> do
      putStrLn $ "│ Rezultat   : " ++ badgeWarn ++ " +++ OK, trecut " ++ show n ++ " teste!"
      putStrLn $ "│ " ++ cRed ++ "VULNERABILITATE CRITICĂ A PBT CLASIC:" ++ cReset
      putStrLn $ "│ QuickCheck raportează 100% SUCCES, deși codul are un BUG GRAV!"
      putStrLn $ "│ Fiind o cutie neagră, QuickCheck nu poate calcula semGen(G) și nu știe"
      putStrLn $ "│ că 66% din spațiul de stări (EUR și USD) a fost complet ignorat!"
    _ -> putStrLn "│ Rezultat neașteptat."
  putStrLn $ "└" ++ replicate 75 '─' ++ "\n"

  -- -------------------------------------------------------------------
  -- TEST 3: Generator Nevalid / Unsound (Fals Negativ / Eșec Spuriu)
  -- -------------------------------------------------------------------
  putStrLn $ cBold ++ "┌── TEST 3: Generator Nevalid (Produce Date Ilegale -> Fals Negativ) ────────" ++ cReset
  putStrLn $ "│ SUT        : encode / decode (cod 100% CORECT)"
  putStrLn $ "│ Generator  : genUnsound (generează ID-uri și sume negative)"
  putStrLn $ "│ Execuție   : QuickCheck testează 'forAll genUnsound'..."
  res3 <- quickCheckWithResult qcArgs (forAll genUnsound (propRoundTrip encode))
  case res3 of
    Failure { reason = r, numShrinks = s } -> do
      putStrLn $ "│ Rezultat   : " ++ badgeFail ++ " *** Eșec după reducerea contraexemplului!"
      putStrLn $ "│ Motiv      : " ++ r
      putStrLn $ "│ Shrinks    : " ++ show s ++ " pași de reducere minimală"
      putStrLn $ "│ " ++ cYellow ++ "PROBLEMĂ METODOLOGICĂ (Fals Negativ):" ++ cReset
      putStrLn $ "│ QuickCheck dă vina pe SUT, deși codul de producție este impecabil!"
      putStrLn $ "│ Generatorul a încălcat precondiția de business (nu este Sound)."
    _ -> putStrLn "│ Rezultat neașteptat."
  putStrLn $ "└" ++ replicate 75 '─' ++ "\n"

  -- -------------------------------------------------------------------
  -- TEST 4: Găsirea Bug-ului Real & Shrinking Automat
  -- -------------------------------------------------------------------
  putStrLn $ cBold ++ "┌── TEST 4: Detecția Bug-ului Real cu Shrinking Nativ QuickCheck ────────────" ++ cReset
  putStrLn $ "│ SUT        : encodeBug (bugul forțat RON)"
  putStrLn $ "│ Generator  : arbitrary (generator complet)"
  putStrLn $ "│ Execuție   : QuickCheck caută contraexemple și le minimizează..."
  res4 <- quickCheckWithResult qcArgs (propRoundTrip encodeBug)
  case res4 of
    Failure { numShrinks = s, numTests = t } -> do
      putStrLn $ "│ Rezultat   : " ++ badgeFail ++ " Bug depistat la testul #" ++ show t
      putStrLn $ "│ Shrinking  : Redus cu succes la contraexemplul minimal (" ++ show s ++ " pași de shrink)."
      putStrLn $ "│ Explicație : QuickCheck a găsit o tranzacție cu EUR/USD și a micșorat-o"
      putStrLn $ "│              până la valoarea cea mai simplă care reproduce eșecul."
    _ -> putStrLn "│ Rezultat neașteptat."
  putStrLn $ "└" ++ replicate 75 '─' ++ "\n"

  putStrLn $ cCyan ++ "╔═════════════════════════════════════════════════════════════════════════════╗" ++ cReset
  putStrLn $ cCyan ++ "║ SINTETIZARE COMPARATIVĂ:                                                    ║" ++ cReset
  putStrLn $ cCyan ++ "║   • Test.QuickCheck (Haskell) = excelent la generare și shrinking, dar      ║" ++ cReset
  putStrLn $ cCyan ++ "║     este o CUTIE NEAGRĂ (nu poate certifica completitudinea).              ║" ++ cReset
  putStrLn $ cCyan ++ "║   • Foundational PBT (ITP 2015) = adaugă semGen(G) și teoreme formale,      ║" ++ cReset
  putStrLn $ cCyan ++ "║     garantând matematic acoperirea și corectitudinea generatorului.         ║" ++ cReset
  putStrLn $ cCyan ++ "╚═════════════════════════════════════════════════════════════════════════════╝" ++ cReset
  putStrLn ""
