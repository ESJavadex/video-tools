import React from 'react';
import { CheckSquare, AlertCircle, Clock, Copy, Check } from 'lucide-react';

interface ActionItem {
  action: string;
  context: string;
  priority: string;
}

interface ActionItemsPanelProps {
  actionItems: ActionItem[];
}

const ActionItemsPanel: React.FC<ActionItemsPanelProps> = ({ actionItems }) => {
  const [copiedIndex, setCopiedIndex] = React.useState<number | null>(null);

  if (!actionItems || actionItems.length === 0) {
    return null;
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'alta':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'media':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <CheckSquare className="w-4 h-4 text-green-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'alta':
        return 'bg-red-50 border-red-200 text-red-700';
      case 'media':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      default:
        return 'bg-green-50 border-green-200 text-green-700';
    }
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const copyAllItems = () => {
    const allItems = actionItems
      .map(item => `• ${item.action} (${item.priority}): ${item.context}`)
      .join('\n');
    navigator.clipboard.writeText(allItems);
    setCopiedIndex(-1);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <CheckSquare className="w-5 h-5 text-blue-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-800">
            Acciones pendientes
          </h3>
          <span className="ml-2 text-sm text-gray-500">
            ({actionItems.length})
          </span>
        </div>
        <button
          onClick={copyAllItems}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
        >
          {copiedIndex === -1 ? (
            <Check className="w-4 h-4 mr-1" />
          ) : (
            <Copy className="w-4 h-4 mr-1" />
          )}
          Copiar todo
        </button>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        Cosas que mencionaste que harías después:
      </p>

      <div className="space-y-3">
        {actionItems.map((item, index) => (
          <div
            key={index}
            className={`border rounded-lg p-4 ${getPriorityColor(item.priority)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  {getPriorityIcon(item.priority)}
                  <span className="ml-2 font-medium text-gray-800">
                    {item.action}
                  </span>
                  <span className="ml-2 text-xs px-2 py-1 rounded-full bg-white bg-opacity-60">
                    Prioridad: {item.priority}
                  </span>
                </div>
                <p className="text-sm text-gray-600 ml-6">
                  {item.context}
                </p>
              </div>
              <button
                onClick={() => copyToClipboard(item.action, index)}
                className="ml-2 text-gray-500 hover:text-gray-700"
                title="Copiar acción"
              >
                {copiedIndex === index ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-700">
          💡 <strong>Consejo:</strong> Revisa estas acciones después de publicar tu video
          para asegurarte de cumplir con todo lo prometido.
        </p>
      </div>
    </div>
  );
};

export default ActionItemsPanel;