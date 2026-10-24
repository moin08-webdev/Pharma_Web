import React from "react";

interface MoneyProps {
  paise: number | null | undefined;
  className?: string;
  showZero?: boolean;
}

export function Money({ paise, className = "", showZero = false }: MoneyProps) {
  if (paise === null || paise === undefined) {
    return <span className={`text-gray-400 font-mono ${className}`}>—</span>;
  }
  if (paise === 0 && !showZero) {
    return <span className={`text-gray-400 font-mono ${className}`}>₹0.00</span>;
  }

  const inr = (paise / 100).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <span className={`font-mono font-medium tracking-tight ${className}`}>
      ₹{inr}
    </span>
  );
}
