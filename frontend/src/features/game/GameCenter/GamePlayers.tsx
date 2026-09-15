type Player = {
  id: number;
  name: string;
  type: "human" | "ai";
};

type Props = {
  players?: Player[];
};

export default function GamePlayers({ players = [] }: Props) {
  if (!players.length) return null;

  return (
    <div className="players">
      <div className="playersTitle">Gracze</div>

      {players.map((p) => (
        <div key={p.id} className={`player ${p.type}`}>
          {p.name}
          {p.type === "ai" && " 🤖"}
        </div>
      ))}
    </div>
  );
}