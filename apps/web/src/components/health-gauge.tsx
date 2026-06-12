"use client";

import { useEffect, useState } from "react";

interface HealthGaugeProps {
  score: number;
  recommendation?: string;
  steamAppId?: number | null;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "#70e38b";
  if (score >= 60) return "#e6c84f";
  if (score >= 40) return "#f59e0b";
  return "#ef4444";
}

function getScoreBg(score: number): string {
  if (score >= 80) return "bg-healthy/10";
  if (score >= 60) return "bg-playable/10";
  if (score >= 40) return "bg-warning/10";
  return "bg-danger/10";
}

function getScoreText(score: number): string {
  if (score >= 80) return "text-healthy";
  if (score >= 60) return "text-playable";
  if (score >= 40) return "text-warning";
  return "text-danger";
}

function getScoreBorder(score: number): string {
  if (score >= 80) return "border-healthy/30";
  if (score >= 60) return "border-playable/30";
  if (score >= 40) return "border-warning/30";
  return "border-danger/30";
}

export function HealthGauge({
  score,
  recommendation,
  steamAppId,
  size = 160,
  strokeWidth = 8,
  showLabel = true,
}: HealthGaugeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (displayScore / 100) * circumference;
  const color = getScoreColor(score);
  const textColor = getScoreText(score);
  const bgColor = getScoreBg(score);
  const borderColor = getScoreBorder(score);

  useEffect(() => {
    const timer = setTimeout(() => setDisplayScore(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const steamUrl = steamAppId
    ? `https://store.steampowered.com/app/${steamAppId}/`
    : null;

  const recContent = showLabel && recommendation ? (
    steamUrl ? (
      <a
        href={steamUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={`text-[10px] leading-none font-pixel px-2 py-1.5 border ${borderColor} ${bgColor} ${textColor} rounded hover:opacity-80 transition-opacity tracking-tighter`}
      >
        {recommendation}
      </a>
    ) : (
      <span className={`text-[10px] leading-none font-pixel px-2 py-1.5 ${bgColor} ${textColor} rounded tracking-tighter`}>
        {recommendation}
      </span>
    )
  ) : null;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="rotate-[-90deg]">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1a1a1a"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          className="gauge-fill"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-1">
        <span className={`font-display text-4xl ${textColor}`}>
          {displayScore}
        </span>
        {recContent}
      </div>
    </div>
  );
}

export function HealthBadge({
  score,
  recommendation,
  steamAppId,
}: {
  score: number;
  recommendation?: string;
  steamAppId?: number | null;
}) {
  const text = getScoreText(score);
  const bg = getScoreBg(score);
  const border = getScoreBorder(score);
  const steamUrl = steamAppId
    ? `https://store.steampowered.com/app/${steamAppId}/`
    : null;

  const badge = (
    <span className={`inline-flex items-center gap-2 px-2.5 py-1 rounded ${bg} ${text} ${steamUrl ? `border ${border}` : ""}`}>
      <span className="font-display text-lg leading-none">{score}</span>
      {recommendation && (
        <span className="font-pixel text-[8px] leading-none tracking-tighter">
          {recommendation}
        </span>
      )}
    </span>
  );

  return steamUrl ? (
    <a href={steamUrl} target="_blank" rel="noopener noreferrer" className="hover:opacity-80 transition-opacity">
      {badge}
    </a>
  ) : (
    badge
  );
}
