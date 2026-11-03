import React from "react";

interface AppLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  showText?: boolean;
  showTagline?: boolean;
  className?: string;
  textClassName?: string;
}

export function AppLogo({
  size = "md",
  showText = true,
  showTagline = false,
  className = "",
  textClassName = "text-gray-900",
}: AppLogoProps) {
  const sizeMap = {
    sm: "w-7 h-7",
    md: "w-9 h-9",
    lg: "w-12 h-12",
    xl: "w-16 h-16",
  };

  const titleSizeMap = {
    sm: "text-base",
    md: "text-lg",
    lg: "text-2xl",
    xl: "text-3xl",
  };

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <img
        src="/logo.png"
        alt="PharmaBridge Logo"
        className={`${sizeMap[size]} object-contain rounded-lg shadow-sm shrink-0`}
      />
      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className={`font-bold tracking-tight ${titleSizeMap[size]} ${textClassName}`}>
              PharmaBridge
            </span>
            <span className="hidden sm:inline-block text-[10px] font-bold px-1.5 py-0.5 bg-teal-50 text-teal-800 rounded border border-teal-200">
              v1.0
            </span>
          </div>
          {showTagline && (
            <span className="text-[11px] text-gray-500 font-medium">
              Clinical Pharmacy Workspace
            </span>
          )}
        </div>
      )}
    </div>
  );
}
