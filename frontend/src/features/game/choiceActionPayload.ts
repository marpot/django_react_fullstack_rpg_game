export type GameAction =
  | "attack"
  | "move"
  | "inspect"
  | "talk"
  | "defend"
  | "use_item";

export type GameCommand = {
  action: GameAction;
  target: string | null;
  method: string | null;
};

export type StructuredChoice = {
  id?: string;
  label?: string;
  title?: string;
  message?: string;
  action: GameAction;
  target?: string | null;
  method?: string | null;
};

export type ChoiceActionPayload = {
  type: "player_action";
  command: GameCommand;
};

export function choiceActionPayload(choice: StructuredChoice): ChoiceActionPayload {
  return {
    type: "player_action",
    command: {
      action: choice.action,
      target: choice.target ?? null,
      method: choice.method ?? null,
    },
  };
}
