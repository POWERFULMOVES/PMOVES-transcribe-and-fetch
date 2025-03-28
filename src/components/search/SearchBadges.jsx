import React, { useState, useEffect } from 'react';
import { 
  getMethodStyle, 
  getSourceStyle, 
  getScoreStyle 
} from '@/lib/search-styles';

/**
 * Badge component for displaying search method with enhanced styling and animations
 */
export function MethodBadge({ method, animate = false, delay = 0 }) {
  const [animateIn, setAnimateIn] = useState(!animate);
  const style = getMethodStyle(method);
  
  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimateIn(true);
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [animate, delay]);
  
  return (
    <span 
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs 
        ${style.bgColor} ${style.textColor} border ${style.borderColor || 'border-transparent'} 
        shadow-sm transition-all duration-300 hover:shadow
      `}
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'scale(1)' : 'scale(0.9)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span className="mr-1">{style.icon}</span>
      {style.title}
    </span>
  );
}

/**
 * Badge component for displaying content source with enhanced styling and animations
 */
export function SourceBadge({ source, animate = false, delay = 0 }) {
  const [animateIn, setAnimateIn] = useState(!animate);
  const style = getSourceStyle(source);
  
  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimateIn(true);
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [animate, delay]);
  
  return (
    <span 
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs 
        ${style.bgColor} ${style.textColor} border ${style.borderColor || 'border-transparent'} 
        shadow-sm transition-all duration-300 hover:shadow
      `}
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'scale(1)' : 'scale(0.9)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span className="mr-1">{style.icon}</span>
      {style.title}
    </span>
  );
}

/**
 * Badge component for displaying similarity score with enhanced styling and animations
 */
export function ScoreBadge({ score, animate = false, delay = 0 }) {
  const [animateIn, setAnimateIn] = useState(!animate);
  const style = getScoreStyle(score);
  const formattedScore = typeof score === 'number' ? score.toFixed(3) : 'N/A';
  
  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimateIn(true);
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [animate, delay]);
  
  // Determine score icon based on value
  const scoreIcon = typeof score === 'number' 
    ? (score >= 0.8 ? '🔥' : score >= 0.6 ? '✨' : '📊') 
    : '❓';
  
  return (
    <span 
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-md text-xs 
        ${style.bgColor} ${style.textColor} ${style.fontWeight} 
        border border-gray-200 shadow-sm transition-all duration-300 hover:shadow
      `}
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'scale(1)' : 'scale(0.9)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span className="mr-1">{scoreIcon}</span>
      {formattedScore}
      <span className="ml-1 text-xs opacity-75">({style.description})</span>
    </span>
  );
}

/**
 * Badge component for displaying timestamp information with enhanced styling
 */
export function TimestampBadge({ startTime, endTime, animate = false, delay = 0 }) {
  const [animateIn, setAnimateIn] = useState(!animate);
  
  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimateIn(true);
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [animate, delay]);
  
  if (!startTime && !endTime) return null;
  
  return (
    <span 
      className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs bg-cyan-50 text-cyan-700 border border-cyan-200 shadow-sm transition-all duration-300 hover:shadow"
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'scale(1)' : 'scale(0.9)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span className="mr-1">⏱️</span>
      {startTime || '0:00'} - {endTime || 'end'}
    </span>
  );
}

/**
 * Badge component for displaying segment ID with enhanced styling
 */
export function SegmentBadge({ segmentId, animate = false, delay = 0 }) {
  const [animateIn, setAnimateIn] = useState(!animate);
  
  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimateIn(true);
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [animate, delay]);
  
  if (!segmentId && segmentId !== 0) return null;
  
  return (
    <span 
      className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs bg-yellow-50 text-yellow-700 border border-yellow-200 shadow-sm transition-all duration-300 hover:shadow"
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'scale(1)' : 'scale(0.9)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span className="mr-1">🔢</span>
      Segment {segmentId}
    </span>
  );
}

/**
 * Badge component for displaying word count with enhanced styling
 */
export function WordCountBadge({ count, animate = false, delay = 0 }) {
  const [animateIn, setAnimateIn] = useState(!animate);
  
  useEffect(() => {
    if (animate) {
      const timer = setTimeout(() => {
        setAnimateIn(true);
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [animate, delay]);
  
  if (!count) return null;
  
  // Determine size category
  let sizeCategory = 'small';
  let sizeIcon = '📝';
  
  if (count > 500) {
    sizeCategory = 'large';
    sizeIcon = '📚';
  } else if (count > 100) {
    sizeCategory = 'medium';
    sizeIcon = '📄';
  }
  
  return (
    <span 
      className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs bg-gray-100 text-gray-700 border border-gray-200 shadow-sm transition-all duration-300 hover:shadow"
      style={{ 
        opacity: animateIn ? 1 : 0,
        transform: animateIn ? 'scale(1)' : 'scale(0.9)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span className="mr-1">{sizeIcon}</span>
      {count} words
      <span className="ml-1 text-xs opacity-75">({sizeCategory})</span>
    </span>
  );
}
