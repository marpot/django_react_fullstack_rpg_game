type RetryConfig = {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs?: number;
  factor?: number;
};

type RetryContext = {
  attempt: number;
  delay: number;
};

export class ChatReconnect {
  private config: RetryConfig;
  private attempt = 0;
  private timeoutId: ReturnType<typeof setTimeout> | null = null;
  private stopped = false;

  private reconnectFn: (() => void) | null = null;

  constructor(config?: Partial<RetryConfig>) {
    this.config = {
      maxRetries: config?.maxRetries ?? 10,
      baseDelayMs: config?.baseDelayMs ?? 1000,
      maxDelayMs: config?.maxDelayMs ?? 15000,
      factor: config?.factor ?? 2,
    };
  }

  // =========================
  // PUBLIC API (HOOK FRIENDLY)
  // =========================

  scheduleReconnect() {
    if (!this.reconnectFn) return;
    this.start(this.reconnectFn);
  }

  reset() {
    this.stop();
  }

  // =========================
  // CORE
  // =========================

  start(reconnectFn: () => void) {
    this.reconnectFn = reconnectFn;
    this.stopped = false;
    this.attempt = 0;
    this.schedule();
  }

  stop() {
    this.stopped = true;

    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    this.attempt = 0;
  }

  private schedule() {
    if (this.stopped || !this.reconnectFn) return;

    if (this.attempt >= this.config.maxRetries) {
      console.warn("[ChatReconnect] max retries reached");
      return;
    }

    const delay = this.calculateDelay({
      attempt: this.attempt,
      delay: this.config.baseDelayMs,
    });

    this.timeoutId = setTimeout(() => {
      if (this.stopped) return;

      this.attempt++;
      this.reconnectFn?.();
      this.schedule();
    }, delay);
  }

  private calculateDelay(ctx: RetryContext): number {
    const factor = this.config.factor ?? 2;

    const delay = ctx.delay * Math.pow(factor, ctx.attempt);

    return Math.min(delay, this.config.maxDelayMs ?? delay);
  }
}