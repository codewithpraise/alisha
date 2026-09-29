import { 
  ResponseMode, 
  RetrievalNeed, 
  MemoryNeed, 
  InteractionMode, 
  ResponseAct, 
  LayaDecision, 
  ResponseBehaviorPlan 
} from './types';

export class LayaRouter {
  evaluateState(message: string, isVoice: boolean = false): LayaDecision {
    const msg = message.trim().toLowerCase();

    if (isVoice) {
      return {
        responseMode: 'CALL',
        retrievalNeed: 'LIGHT',
        memoryNeed: 'NONE',
        interactionMode: 'CASUAL',
        responseAct: 'ANSWER',
        historicalReference: false,
        confidence: 0.98
      };
    }

    // Memory Need
    let memNeed: MemoryNeed = 'NONE';
    if (/\b(remember that|don't forget|keep in mind|note that|my (exam|birthday) is)\b/.test(msg)) {
      memNeed = 'WRITE';
    } else if (/\b(what did i (say|tell you)|do you remember (my|what|when))\b/.test(msg)) {
      memNeed = 'RECALL';
    } else if (/\b(actually it'?s|correction|changed to)\b/.test(msg)) {
      memNeed = 'UPDATE';
    } else if (/\b(forget (that|about|what)|delete (that|memory))\b/.test(msg)) {
      memNeed = 'FORGET';
    }

    // Fast Casual vs Deep
    const fastRegex = /^(yo|hey|hi|hello|heyy+|sup|wyd|wbu|lol|lmao|same|omg|damn|bruh|cuh|innit|yeah|nah|wait|good morning|gm|gn|k|hmm)$/;
    const isFast = fastRegex.test(msg) || (msg.split(/\s+/).length <= 3 && !/\b(remember|why|explain)\b/.test(msg));
    
    const deepRegex = /\b(remember (when|that time)|why do you think|i feel (sad|anxious|lost|stressed)|biochem|exam prep)\b/;
    const isDeep = deepRegex.test(msg) || msg.split(/\s+/).length > 15 || memNeed !== 'NONE';

    const responseMode: ResponseMode = isDeep ? 'DEEP' : (isFast ? 'FAST' : 'FAST');
    const retrievalNeed: RetrievalNeed = isDeep ? 'DEEP' : (isFast ? 'NONE' : 'LIGHT');

    // Interaction Mode
    let interactionMode: InteractionMode = 'CASUAL';
    if (/\b(love you|miss you|pookie|cutie|babycakes|boo)\b/.test(msg)) {
      interactionMode = 'AFFECTIONATE';
    } else if (/\b(loser|noob|dumb|fool|joke|cap|💀|😭)\b/.test(msg)) {
      interactionMode = /\b(loser|dumb|noob)\b/.test(msg) ? 'TEASING' : 'PLAYFUL';
    } else if (/\b(sad|crying|depressed|hard|difficult|scared)\b/.test(msg)) {
      interactionMode = 'SUPPORTIVE';
    } else if (/\b(serious|urgent|listen)\b/.test(msg)) {
      interactionMode = 'SERIOUS';
    } else if (/\b(omg|omdssd|wow|yay|won|celebrate)\b/.test(msg)) {
      interactionMode = 'EXCITED';
    } else if (/\b(bye|cya|see you|goodnight)\b/.test(msg)) {
      interactionMode = 'FAREWELL';
    }

    // Response Act
    let responseAct: ResponseAct = 'REACTION';
    if (/^(yo|hey|hi|hello|heyy+|gm|good morning)/.test(msg)) {
      responseAct = 'GREETING';
    } else if (/^(bye|gn|goodnight|see ya)/.test(msg)) {
      responseAct = 'FAREWELL';
    } else if (/\b(loser|shut up|ugly)\b/.test(msg)) {
      responseAct = 'PLAYFUL_INSULT';
    } else if (/\b(why|what|how|when|where)\b/.test(msg) && msg.endsWith('?')) {
      responseAct = 'ANSWER';
    } else if (interactionMode === 'SUPPORTIVE') {
      responseAct = 'REASSURANCE';
    } else if (interactionMode === 'AFFECTIONATE') {
      responseAct = 'AFFECTION';
    } else if (interactionMode === 'TEASING') {
      responseAct = 'TEASE';
    }

    const historicalReference = /\b(remember (when|that time)|that cat|the lab|chemistry practical)\b/.test(msg);
    const confidence = isFast || isDeep ? 0.92 : 0.78;

    return {
      responseMode,
      retrievalNeed,
      memoryNeed: memNeed,
      interactionMode,
      responseAct,
      historicalReference,
      confidence
    };
  }

  buildBehaviorPlan(decision: LayaDecision): ResponseBehaviorPlan {
    const isFast = decision.responseMode === 'FAST';
    return {
      mode: decision.interactionMode,
      speechAct: decision.responseAct,
      lengthClass: isFast ? 'VERY_SHORT' : 'MEDIUM',
      targetWordRange: isFast ? [2, 8] : [8, 22],
      targetBubbleCount: isFast ? 1 : 2,
      slangIntensity: 0.85,
      emojiPolicy: decision.interactionMode === 'EXCITED' ? 'REQUIRED_ONE' : 'OPTIONAL',
      warmth: decision.interactionMode === 'SUPPORTIVE' ? 0.9 : 0.6,
      teasingIntensity: decision.interactionMode === 'TEASING' ? 0.8 : 0.2,
      relevantFacts: [],
      relevantMemories: [],
      historicalExamples: [],
      guidanceNotes: `Mode: ${decision.interactionMode}. Speech act: ${decision.responseAct}.`
    };
  }
}
