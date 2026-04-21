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
 * Tries to match the level's difficulty weights, but falls back to adjacent
 * difficulty tiers when a tier has no questions. Recycles from the pool
 * (with shuffling) when the available questions are fewer than needed.
 */
export function selectQuestionsForLevel(
  level: GameLevel,
  allQuestions: Question[],
): Question[] {
  const byDiff: Record<Difficulty, Question[]> = {
    easy: [],
    medium: [],
    hard: [],
    very_hard: [],
    expert: [],
  };
  for (const q of allQuestions) {
    byDiff[q.difficulty].push(q);
  }

  // Compute how many questions we want from each difficulty
  const totalWeight = Object.values(level.difficultyWeights).reduce(
    (a, b) => a + b,
    0,
  );
  if (totalWeight === 0) return shuffle(allQuestions).slice(0, level.questionsPerRound);

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

  const selected: Question[] = [];

  for (const { difficulty, count } of targets) {
    // Build a fallback chain: prefer exact difficulty, then adjacent tiers
    const idx = DIFFICULTY_ORDER.indexOf(difficulty);
    const fallbackOrder = [difficulty];
    for (let dist = 1; dist < DIFFICULTY_ORDER.length; dist++) {
      if (idx + dist < DIFFICULTY_ORDER.length)
        fallbackOrder.push(DIFFICULTY_ORDER[idx + dist]);
      if (idx - dist >= 0)
        fallbackOrder.push(DIFFICULTY_ORDER[idx - dist]);
    }

    let pool: Question[] = [];
    for (const d of fallbackOrder) {
      if (byDiff[d].length > 0) {
        pool = byDiff[d];
        break;
      }
    }

    if (pool.length === 0) continue; // no questions at all — shouldn't happen

    const shuffled = shuffle(pool);
    for (let i = 0; i < count; i++) {
      selected.push(shuffled[i % shuffled.length]);
    }
  }

  // Safety: if we still don't have enough, fill from the full pool
  if (selected.length < level.questionsPerRound) {
    const all = shuffle(allQuestions);
    while (selected.length < level.questionsPerRound) {
      selected.push(all[selected.length % all.length]);
    }
  }

  return shuffle(selected);
}
