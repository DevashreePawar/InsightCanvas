import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { trackEvent } from '../utils/analytics';

const pageEvents = {
  '/': 'landing_view',
  '/dashboard': 'dashboard_view',
  '/sessions': 'sessions_view',
  '/usage': 'usage_view',
};

export default function AnalyticsTracker() {
  const location = useLocation();

  useEffect(() => {
    const eventName = location.pathname.startsWith('/share/')
      ? 'shared_dashboard_view'
      : pageEvents[location.pathname] || 'page_view';
    trackEvent(eventName, {}, location.pathname);
  }, [location.pathname]);

  return null;
}
