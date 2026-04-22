import type { Difficulty, Question } from './types';

export type GameLevel = {
  level: number;
  name: string;
  description: string;
  /** Relative weights for each difficulty tier */
  difficultyWeights: Record<Difficulty, number>;
  questionsPerRound: number;
  passThreshold: number;
};

export const GAME_LEVELS: GameLevel[] = [
  {
    level: 1,
    name: 'Rookie',
    description: 'Warm up with the basics.',
    difficultyWeights: { easy: 1, medium: 0, hard: 0, very_hard: 0, expert: 0 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
  {
    level: 2,
    name: 'Student',
    description: 'A step up — some trickier questions mixed in.',
    difficultyWeights: { easy: 0.6, medium: 0.4, hard: 0, very_hard: 0, expert: 0 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
  {
    level: 3,
    name: 'Analyst',
    description: "You'll need real knowledge now.",
    difficultyWeights: { easy: 0.2, medium: 0.6, hard: 0.2, very_hard: 0, expert: 0 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
  {
    level: 4,
    name: 'Expert',
    description: 'The questions get serious.',
    difficultyWeights: { easy: 0, medium: 0.3, hard: 0.5, very_hard: 0.2, expert: 0 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
  {
    level: 5,
    name: 'Strategist',
    description: 'Only the well-read survive here.',
    difficultyWeights: { easy: 0, medium: 0, hard: 0.5, very_hard: 0.4, expert: 0.1 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
  {
    level: 6,
    name: 'Mastermind',
    description: 'Deep expertise required.',
    difficultyWeights: { easy: 0, medium: 0, hard: 0.2, very_hard: 0.5, expert: 0.3 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
  {
    level: 7,
    name: 'Grandmaster',
    description: "The hardest questions we've got. Good luck.",
    difficultyWeights: { easy: 0, medium: 0, hard: 0, very_hard: 0.5, expert: 0.5 },
    questionsPerRound: 10,
    passThreshold: 8,
  },
];

/** Fisher–Yates shuffle (returns new array) */
function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const DIFFICULTY_ORDER: Difficulty[] = ['easy', 'medium', 'hard', 'very_hard', 'expert'];

/**
 * Select questions for a game level.
 *
 * Honors `excludeIds` so a question already shown earlier in the same game
 * session is not shown again (JGM's no-repeat-within-session rule).
 *
 * When a targeted difficulty bucket is exhausted, falls back to the nearest
 * EASIER tier first (then harder) so early-level difficulty doesn't silently
 * inflate under narrow filters. If no questions remain at any tier the level
 * may fall short, but we never duplicate within a round and never recycle
 * ids already seen this session unless the whole session pool is exhausted.
 */
export function selectQuestionsForLevel(
  level: GameLevel,
  allQuestions: Question[],
  excludeIds: ReadonlySet<string> = new Set(),
): Question[] {
  const available = allQuestions.filter((q) => !excludeIds.has(q.id));

  // If excluding leaves too few to fill the round, fall back to the full pool
  // so the player doesn't hit a dead end. This only kicks in after the session
  // has effectively exhausted the filtered bank.
  const sourcePool =
    available.length >= level.questionsPerRound ? available : allQuestions;

  const byDiff: Record<Difficulty, Question[]> = {
    easy: [],
    medium: [],
    hard: [],
    very_hard: [],
    expert: [],
  };
  for (const q of sourcePool) {
    byDiff[q.difficulty].push(q);
  }

  const totalWeight = Object.values(level.difficultyWeights).reduce(
    (a, b) => a + b,
    0,
  );
  if (totalWeight === 0) {
    return shuffle(sourcePool).slice(0, level.questionsPerRound);
  }

  const targets: { difficulty: Difficulty; count: number }[] = [];
  let allocated = 0;
  const entries = DIFFICULTY_ORDER.filter(
    (d) => level.difficultyWeights[d] > 0,
  );

  for (let i = 0; i < entries.length; i++) {
    const d = entries[i];
    const w = level.difficultyWeights[d];
    const isLast = i === entries.length - 1;
    const count = isLast
      ? level.questionsPerRound - allocated
      : Math.round((w / totalWeight) * level.questionsPerRound);
    targets.push({ difficulty: d, count });
    allocated += count;
  }

  const chosen: Question[] = [];
  const chosenIds = new Set<string>();

  const take = (pool: Question[], n: number) => {
    for (const q of pool) {
      if (n <= 0) break;
      if (chosenIds.has(q.id)) continue;
      chosen.push(q);
      chosenIds.add(q.id);
      n -= 1;
    }
    return n;
  };

  for (const { difficulty, count } of targets) {
    // Fallback chain: target tier → easier tiers (desc) → harder tiers (asc).
    // Preferring easier first keeps early-level difficulty from silently
    // inflating when the targeted bucket is empty under narrow filters.
    const idx = DIFFICULTY_ORDER.indexOf(difficulty);
    const fallbackOrder: Difficulty[] = [difficulty];
    for (let dist = 1; dist < DIFFICULTY_ORDER.length; dist++) {
      if (idx - dist >= 0) fallbackOrder.push(DIFFICULTY_ORDER[idx - dist]);
    }
    for (let dist = 1; dist < DIFFICULTY_ORDER.length; dist++) {
      if (idx + dist < DIFFICULTY_ORDER.length)
        fallbackOrder.push(DIFFICULTY_ORDER[idx + dist]);
    }

    let remaining = count;
    for (const d of fallbackOrder) {
      if (remaining <= 0) break;
      if (byDiff[d].length === 0) continue;
      remaining = take(shuffle(byDiff[d]), remaining);
    }
  }

  // Safety net: if any gaps remain, fill from the whole source pool without duplicates.
  if (chosen.length < level.questionsPerRound) {
    const remaining = shuffle(sourcePool).filter((q) => !chosenIds.has(q.id));
    for (const q of remaining) {
      if (chosen.length >= level.questionsPerRound) break;
      chosen.push(q);
      chosenIds.add(q.id);
    }
  }

  return shuffle(chosen);
}
