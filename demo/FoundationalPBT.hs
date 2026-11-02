{-|
Module      : FoundationalPBT
Description : Motorul formal de Foundational Property-Based Testing (FPBT)
Reference   : Zoe Paraskevopoulou, Cătălin Hrițcu, Maxime Dénès,
              Leonidas Lampropoulos, Benjamin C. Pierce
              "Foundational Property-Based Testing" (ITP 2015)

Acest modul implementează conceptul central din articol:
  În loc ca un generator de teste să fie o «cutie neagră» probabilistică opacă,
  el este dotat cu o semantică matematică denotațională exactă: semGen(G).
  Aceasta permite verificarea formală a codului de testare înainte de rulare.
-}
module FoundationalPBT
  ( -- * 1. Tipul Generatorului Foundational
    FGen(..)
  , semGen

    -- * 2. Generatorul de Numere Pseudo-Aleatorii (PRNG)
  , Seed
  , mkSeed

    -- * 3. Combinatori Monadici
  , elements
  , sampleMany

    -- * 4. Verificarea Celor Trei Teoreme Formale
  , Soundness(..)
  , Completeness(..)
  , Fidelity(..)
  , verifySoundness
  , verifyCompleteness
  , verifyFidelity

    -- * 5. Pipeline-ul de Testare Certificată
  , Outcome(..)
  , runCertifiedTest
  ) where

import Data.Set (Set)
import qualified Data.Set as Set
import Data.Word (Word64)

-- =====================================================================
-- 1. Generatorul Pseudo-Aleator (PRNG Determinist)
-- =====================================================================

-- | Seed pentru generatorul pseudo-aleator liniar congruențial (LCG 64-bit).
-- Permite teste 100% reproductibile, fără a depinde de pachete externe.
newtype Seed = Seed Word64
  deriving (Eq, Show)

-- | Inițializarea unui seed (folosește o valoare non-nulă implicită).
mkSeed :: Word64 -> Seed
mkSeed 0 = Seed 0x853c49e6748fea9b
mkSeed w = Seed w

-- | Produce un întreg aleator în intervalul [lo, hi] și returnează noul Seed.
nextRange :: (Int, Int) -> Seed -> (Int, Seed)
nextRange (lo, hi) (Seed s) =
  let -- Pasul standard LCG (constantele lui Knuth pentru 64-bit)
      s'    = s * 6364136223846793005 + 1442695040888963407
      range = fromIntegral (hi - lo + 1)
      val   = lo + fromIntegral (s' `mod` range)
  in (val, Seed s')

-- =====================================================================
-- 2. Tipul FGen: Eșantionare + Semantică Denotațională
-- =====================================================================

-- | 'FGen a' este tipul central din Foundational PBT.
-- Spre deosebire de QuickCheck (unde Gen a = Seed -> a este o cutie neagră),
-- FGen păstrează două interpretări simultane:
--
--   1. 'sampleOne': componenta executabilă (extrage o valoare pseudo-aleatorie).
--   2. 'rawSupport': componenta matematică (cunoaște mulțimea valorilor posibile).
data FGen a = FGen
  { sampleOne  :: Seed -> (a, Seed)  -- ^ Funcția de eșantionare aleatorie
  , rawSupport :: [a]                 -- ^ Lista tuturor rezultatelor posibile
  }

-- | Semantica possibilistică din articol: semGen(G).
-- Calculează mulțimea matematică (fără duplicate) a tuturor stărilor
-- pe care generatorul le poate produce cu probabilitate nenulă:
--   semGen(G) = { x | P(G produce x) > 0 }
semGen :: Ord a => FGen a -> Set a
semGen = Set.fromList . rawSupport

-- =====================================================================
-- 3. Instanțe Monadice (Permit compunerea generatoarelor)
-- =====================================================================

-- | Functor: aplicarea unei funcții transformă atât eșantionul, cât și suportul.
instance Functor FGen where
  fmap f (FGen smp supp) =
    FGen (\s -> let (x, s') = smp s in (f x, s'))
         (map f supp)

-- | Applicative: combinarea a două generatoare independente.
-- Suportul matematic devine produsul cartezian al posibilităților celor două.
instance Applicative FGen where
  pure x = FGen (\s -> (x, s)) [x]

  FGen sf suppF <*> FGen sx suppX =
    FGen
      (\s ->
         let (f, s1) = sf s
             (x, s2) = sx s1
         in (f x, s2))
      [f x | f <- suppF, x <- suppX]

-- | Monad: generare secvențială/dependentă.
-- Definiția semGen pentru Bind (>>=) transpune exact Teorema din articol:
--   semGen (G >>= f) = ⋃ { semGen (f x) | x ∈ semGen(G) }
instance Monad FGen where
  return = pure

  FGen sx suppX >>= f =
    FGen
      (\s ->
         let (x, s1) = sx s
         in sampleOne (f x) s1)
      (concatMap (rawSupport . f) suppX)

-- =====================================================================
-- 4. Combinatori de Bază
-- =====================================================================

-- | Alege uniform o valoare dintr-o listă nevidă.
-- Suportul denotațional este chiar lista elementelor posibile.
elements :: [a] -> FGen a
elements [] = error "elements: lista nu poate fi goala"
elements xs =
  FGen
    (\s ->
       let (idx, s') = nextRange (0, length xs - 1) s
       in (xs !! idx, s'))
    xs

-- | Extrage o secvență finită de N eșantioane folosind generatorul.
sampleMany :: Int -> FGen a -> Seed -> [a]
sampleMany n gen startSeed = take n (go startSeed)
  where
    go s = let (x, s') = sampleOne gen s in x : go s'

-- =====================================================================
-- 5. Verificarea Teoremelor Formale (Articolul ITP 2015)
-- =====================================================================

-- | Rezultatul verificării Corectitudinii (Soundness).
data Soundness a
  = Sound             -- ^ Toate valorile respectă precondiția
  | Unsound [a]       -- ^ S-au găsit valori generate care încalcă precondiția
  deriving (Eq, Show)

-- | Rezultatul verificării Completitudinii (Completeness / Adequacy).
data Completeness a
  = Complete          -- ^ 100% din domeniul țintă este acoperit
  | Incomplete [a] Double -- ^ Cazuri lipsă din domeniu și procentul de acoperire
  deriving (Eq, Show)

-- | Rezultatul verificării Fidelității Verificatorului (Fidelity).
data Fidelity a
  = Faithful          -- ^ Verificatorul executabil coincide cu specificația logică
  | Divergent [a]     -- ^ Valori pe care verificatorul dă alt răspuns decât specificația
  deriving (Eq, Show)

-- | Teorema 1: Corectitudinea Generatorului (Generator Soundness).
--   semGen(G) ⊆ { x | Preconditie(x) }
-- Garantează că generatorul nu produce date ilegale/gunoi.
verifySoundness :: Ord a => (a -> Bool) -> FGen a -> Soundness a
verifySoundness preconditie gen =
  case filter (not . preconditie) (Set.toList (semGen gen)) of
    []        -> Sound
    ilegale   -> Unsound ilegale

-- | Teorema 2: Completitudinea Generatorului (Generator Completeness).
--   Domeniu ⊆ semGen(G)
-- Garantează că generatorul nu are unghiuri moarte în spațiul de intrare.
verifyCompleteness :: Ord a => Set a -> FGen a -> Completeness a
verifyCompleteness domeniuAsteptat gen =
  let lipsa   = Set.toList (Set.difference domeniuAsteptat (semGen gen))
      total   = Set.size domeniuAsteptat
      acoperit = total - length lipsa
      procent  = if total == 0 then 1.0 else fromIntegral acoperit / fromIntegral total
  in if null lipsa
       then Complete
       else Incomplete lipsa procent

-- | Teorema 3: Fidelitatea Verificatorului (Checker Fidelity).
--   ∀ x ∈ semGen(G). Verificator(x) == Specificatie(x)
-- Garantează că testul executabil nu are deviații față de contractul abstract.
verifyFidelity :: Ord a => (a -> Bool) -> (a -> Bool) -> FGen a -> Fidelity a
verifyFidelity specificatie verificator gen =
  case [x | x <- Set.toList (semGen gen), verificator x /= specificatie x] of
    []        -> Faithful
    dezacord  -> Divergent dezacord

-- =====================================================================
-- 6. Pipeline-ul de Testare Certificată
-- =====================================================================

-- | Rezultatul unei testări certificate cu Foundational PBT.
data Outcome a
  = CertifiedSuccess Int        -- ^ N teste rulate cu succes pe un generator demonstrat complet
  | CertificateRejected String  -- ^ Testarea este RESPINSĂ din start (generator invalid/incomplet)
  | CounterexampleFound a       -- ^ S-a găsit un bug real în codul testat (contraexemplu garantat valid)
  deriving (Eq, Show)

-- | Execută testarea doar după ce toate cele trei teoreme formale sunt validate:
--   1. Generatorul este demonstrat SOUND.
--   2. Generatorul este demonstrat COMPLETE.
--   3. Verificatorul este demonstrat FAITHFUL.
runCertifiedTest
  :: Ord a
  => (a -> Bool)     -- ^ Precondiția de validitate a datelor
  -> Set a           -- ^ Domeniul de acoperit
  -> (a -> Bool)     -- ^ Specificația declarativă abstractă
  -> (a -> Bool)     -- ^ Verificatorul executabil (checker)
  -> FGen a          -- ^ Generatorul de date
  -> Int             -- ^ Numărul de teste de eșantionat
  -> Seed            -- ^ Seed inițial
  -> Outcome a
runCertifiedTest preconditie domeniu specificatie verificator gen nrTeste seed =
  -- Faza 1: Verificarea Corectitudinii Generatorului
  case verifySoundness preconditie gen of
    Unsound bads ->
      CertificateRejected $
        "Generator Nevalid (Unsound)! Produce intrari ilegale: " ++ show (length bads)

    Sound ->
      -- Faza 2: Verificarea Completitudinii Generatorului
      case verifyCompleteness domeniu gen of
        Incomplete lipsa procent ->
          CertificateRejected $
            "Generator Incomplet! Acoperire " ++ show (round (procent * 100) :: Int)
            ++ "%, lipsesc " ++ show (length lipsa) ++ " cazuri din domeniu."

        Complete ->
          -- Faza 3: Verificarea Fidelității Verificatorului
          case verifyFidelity specificatie verificator gen of
            Divergent dezacord ->
              CertificateRejected $
                "Verificator Infidel! Discrepanta pe " ++ show (length dezacord) ++ " cazuri."

            Faithful ->
              -- Faza 4: Eșantionare certificată (avem garanția matematică a testelor)
              case filter (not . verificator) (sampleMany nrTeste gen seed) of
                []    -> CertifiedSuccess nrTeste
                (c:_) -> CounterexampleFound c
