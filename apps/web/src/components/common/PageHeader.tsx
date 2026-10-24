import React from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function PageHeader({ title, description, action }: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-border-light gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-text-light">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-text-muted-light">{description}</p>
        )}
      </div>
      {action && <div className="flex items-center gap-3">{action}</div>}
    </div>
  );
}
