import { LayaRouter } from './LayaRouter';
import { LayaDecision, ResponseBehaviorPlan } from './types';

export class LayaService {
  private static instance: LayaService;
  private router: LayaRouter;

  constructor() {
    this.router = new LayaRouter();
  }

  static getInstance(): LayaService {
    if (!LayaService.instance) {
      LayaService.instance = new LayaService();
    }
    return LayaService.instance;
  }

  routeTurn(message: string, isVoice: boolean = false): { decision: LayaDecision; plan: ResponseBehaviorPlan } {
    const decision = this.router.evaluateState(message, isVoice);
    const plan = this.router.buildBehaviorPlan(decision);
    return { decision, plan };
  }
}
