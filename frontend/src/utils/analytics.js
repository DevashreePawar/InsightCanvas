import { api } from '../services/api';

const VISITOR_KEY = 'insightcanvas_visitor_id';

function createVisitorId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `visitor_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export function getVisitorId() {
  if (typeof window === 'undefined') return 'server-render';
  const existing = window.localStorage.getItem(VISITOR_KEY);
  if (existing) return existing;
  const next = createVisitorId();
  window.localStorage.setItem(VISITOR_KEY, next);
  return next;
}

export function trackEvent(eventName, metadata = {}, page = window.location.pathname) {
  api
    .trackEvent({
      visitor_id: getVisitorId(),
      event_name: eventName,
      page,
      metadata,
    })
    .catch(() => {
      // Analytics should never interrupt the user experience.
    });
}
