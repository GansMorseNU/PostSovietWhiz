import { useEffect, useMemo, useState } from 'react';

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
};

const DISMISS_KEY = 'ps369-install-prompt-dismissed';

function isStandalone(): boolean {
  const navigatorWithStandalone = window.navigator as Navigator & {
    standalone?: boolean;
  };

  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    navigatorWithStandalone.standalone === true
  );
}

function detectPlatform() {
  const ua = window.navigator.userAgent.toLowerCase();

  return {
    isIos: /iphone|ipad|ipod/.test(ua),
    isSafari: /safari/.test(ua) && !/crios|fxios|edgios|opr\//.test(ua),
  };
}

export function InstallPrompt() {
  const [{ isIos, isSafari }] = useState(() => detectPlatform());
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);
  const [installed, setInstalled] = useState(false);
  const [installing, setInstalling] = useState(false);

  useEffect(() => {
    setInstalled(isStandalone());
    setDismissed(window.localStorage.getItem(DISMISS_KEY) === '1');

    const onBeforeInstallPrompt = (event: Event) => {
      event.preventDefault();
      setDeferredPrompt(event as BeforeInstallPromptEvent);
    };

    const onAppInstalled = () => {
      setInstalled(true);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt as EventListener);
    window.addEventListener('appinstalled', onAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt as EventListener);
      window.removeEventListener('appinstalled', onAppInstalled);
    };
  }, []);

  const showIosHelp = useMemo(
    () => isIos && !installed && !dismissed && deferredPrompt === null,
    [deferredPrompt, dismissed, installed, isIos],
  );

  const dismiss = () => {
    setDismissed(true);
    window.localStorage.setItem(DISMISS_KEY, '1');
  };

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    setInstalling(true);
    await deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;

    if (choice.outcome === 'accepted') {
      setInstalled(true);
    }

    setDeferredPrompt(null);
    setInstalling(false);
  };

  if (installed || dismissed || (!deferredPrompt && !showIosHelp)) {
    return null;
  }

  return (
    <div className="install-card">
      <div className="install-copy">
        <p className="install-kicker">Install app</p>
        <h2 className="install-title">Put this quiz on your home screen</h2>
        <p className="install-desc">
          It runs in full-screen mode and is easier for students to reopen like a native app.
        </p>
        <p className="install-steps">
          {deferredPrompt
            ? 'Tap install to add it on Android or desktop browsers that support app install.'
            : isSafari
              ? 'On iPhone or iPad, tap Share and then choose Add to Home Screen.'
              : 'On iPhone or iPad, open this page in Safari, then tap Share and choose Add to Home Screen.'}
        </p>
      </div>

      <div className="install-actions">
        {deferredPrompt && (
          <button className="install-primary" onClick={handleInstall} disabled={installing}>
            {installing ? 'Installing...' : 'Install app'}
          </button>
        )}
        <button className="install-secondary" onClick={dismiss}>
          {deferredPrompt ? 'Not now' : 'Got it'}
        </button>
      </div>
    </div>
  );
}
