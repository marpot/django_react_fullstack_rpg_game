import { useNavigate } from 'react-router-dom'

import '@/styles/pages/settings.scss'

function Settings() {
  const navigate = useNavigate()

  return (
    <main className="settings-page">
      <section className="settings-panel">
        <div className="settings-panel__ornament" aria-hidden="true">
          ✦
        </div>

        <p className="settings-panel__eyebrow">ELDORIA</p>

        <h1 className="settings-panel__title">Ustawienia</h1>

        <div className="settings-panel__divider" aria-hidden="true">
          <span />
          <span className="settings-panel__divider-symbol">◆</span>
          <span />
        </div>

        <p className="settings-panel__description">
          Dodatkowe ustawienia gry pojawią się w przyszłych wersjach Eldorii.
        </p>

        <div className="settings-panel__notice">
          <span className="settings-panel__notice-icon" aria-hidden="true">
            ✦
          </span>

          <div>
            <h2>Komnata jest jeszcze zamknięta</h2>
            <p>
              Trwają przygotowania do udostępnienia kolejnych możliwości
              personalizacji Twojej przygody.
            </p>
          </div>
        </div>

        <button
          className="settings-panel__back-button"
          type="button"
          onClick={() => navigate('/dashboard')}
        >
          Wróć do Sali Przygód
        </button>
      </section>
    </main>
  )
}

export default Settings