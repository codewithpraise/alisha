export type ResponseMode = 'FAST' | 'DEEP' | 'CALL';
export type RetrievalNeed = 'NONE' | 'LIGHT' | 'DEEP';
export type MemoryNeed = 'NONE' | 'RECALL' | 'WRITE' | 'UPDATE' | 'FORGET';
export type InteractionMode = 
  | 'CASUAL' 
  | 'PLAYFUL' 
  | 'TEASING' 
  | 'AFFECTIONATE' 
  | 'SUPPORTIVE' 
  | 'SERIOUS' 
  | 'EXCITED' 
  | 'LOW_ENERGY' 
  | 'FIRM' 
  | 'FAREWELL';

export type ResponseAct = 
  | 'GREETING' 
  | 'REACTION' 
  | 'ANSWER' 
  | 'QUESTION' 
  | 'FOLLOW_UP' 
  | 'TEASE' 
  | 'PLAYFUL_INSULT' 
  | 'AFFECTION' 
  | 'REASSURANCE' 
  | 'COMFORT' 
  | 'ENCOURAGEMENT' 
  | 'HUMOR' 
  | 'EXPLANATION' 
  | 'CORRECTION' 
  | 'ACKNOWLEDGMENT' 
  | 'SURPRISE' 
  | 'EXCITEMENT' 
  | 'TOPIC_SHIFT' 
  | 'FAREWELL';

export interface LayaDecision {
  responseMode: ResponseMode;
  retrievalNeed: RetrievalNeed;
  memoryNeed: MemoryNeed;
  interactionMode: InteractionMode;
  responseAct: ResponseAct;
  historicalReference: boolean;
  confidence: number;
}

export interface ResponseBehaviorPlan {
  mode: InteractionMode;
  speechAct: ResponseAct;
  lengthClass: 'VERY_SHORT' | 'SHORT' | 'MEDIUM';
  targetWordRange: [number, number];
  targetBubbleCount: number;
  slangIntensity: number;
  emojiPolicy: 'OPTIONAL' | 'REQUIRED_ONE' | 'NONE';
  warmth: number;
  teasingIntensity: number;
  relevantFacts: string[];
  relevantMemories: string[];
  historicalExamples: string[];
  guidanceNotes: string;
}
