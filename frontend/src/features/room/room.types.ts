export type Character = {
  id: number;
  name: string;
  level: number;

  health: number;
  max_health: number;

  mana: number;
  max_mana: number;

  strength: number;
  dexterity: number;
  intelligence: number;

  is_active?: boolean;
};