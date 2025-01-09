interface TimelineEvent {
  id: string;
  type: 'created' | 'modified' | 'deadline';
  date: Date;
  description: string;
}

interface DocumentTimelineProps {
  events: TimelineEvent[];
}

export function DocumentTimeline({ events }: DocumentTimelineProps) {
  const sortedEvents = [...events].sort((a, b) => b.date.getTime() - a.date.getTime());

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium">Timeline</h4>
      <div className="space-y-3">
        {sortedEvents.map((event) => (
          <div key={event.id} className="flex items-start gap-3">
            <div className={`w-2 h-2 mt-2 rounded-full ${
              event.type === 'created' ? 'bg-green-500' :
              event.type === 'modified' ? 'bg-blue-500' :
              'bg-red-500'
            }`} />
            <div className="flex-1">
              <div className="text-sm">{event.description}</div>
              <div className="text-xs text-gray-500">
                {event.date.toLocaleDateString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
