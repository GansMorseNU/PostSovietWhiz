export type Choice = {
  text: string;
  correct: boolean;
  note?: string;
};

export type Difficulty = 'easy' | 'medium' | 'hard' | 'very_hard' | 'expert';

export type DifficultyFilter = Difficulty | 'mix';

export type Era = 'soviet' | '1990s' | '2000s' | '2010s_plus';

export type EraFilter = Era | 'all';

export type Country = 'russia' | 'ukraine' | 'both';

export type CountryFilter = Country | 'all';

export type Cohort = 'vintage' | 'classic' | 'recent' | 'fresh';

export type CohortFilter = Cohort | 'all';

export type Visual = {
  kind: 'image';
  url: string;
  alt: string;
  credit?: string;
};

export type Question = {
  id: string;
  category: string;
  subcategory: string;
  type: 'multiple_choice';
  prompt: string;
  choices: Choice[];
  explanation: string;
  difficulty: Difficulty;
  era: Era;
  era_filter_visibility?: Era[];
  country: Country;
  cohort?: Cohort;
  tags: string[];
  sources?: string[];
  last_reviewed_date: string;
  visual?: Visual;
};

export type QuestionBank = {
  schema_version: number;
  questions: Question[];
};

export type Answer = {
  questionId: string;
  chosenIndex: number;
  chosenText: string;
  correct: boolean;
};
