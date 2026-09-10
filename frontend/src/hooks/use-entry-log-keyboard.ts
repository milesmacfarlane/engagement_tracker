/**
 * Hook for Entry Log keyboard navigation
 * Allows Tab, Enter, and arrow keys to navigate between cells
 */

import { useCallback, useRef } from 'react';

export function useEntryLogKeyboard(
  gridData: any[][],
  onValueChange: (row: number, col: number, value: string) => void,
  onSave?: () => void
) {
  const gridRef = useRef<(HTMLInputElement | null)[][]>([]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent, row: number, col: number) => {
      let nextRow = row;
      let nextCol = col;
      let handled = false;

      // Arrow keys for navigation
      if (e.key === 'ArrowDown') {
        nextRow = Math.min(row + 1, gridData.length - 1);
        handled = true;
      } else if (e.key === 'ArrowUp') {
        nextRow = Math.max(row - 1, 0);
        handled = true;
      } else if (e.key === 'ArrowRight') {
        nextCol = Math.min(col + 1, gridData[0].length - 1);
        handled = true;
      } else if (e.key === 'ArrowLeft') {
        nextCol = Math.max(col - 1, 0);
        handled = true;
      }
      // Tab for forward navigation
      else if (e.key === 'Tab') {
        e.preventDefault();
        if (e.shiftKey) {
          // Shift+Tab - go backwards
          if (col > 0) {
            nextCol = col - 1;
          } else if (row > 0) {
            nextRow = row - 1;
            nextCol = gridData[row - 1].length - 1;
          }
        } else {
          // Tab - go forwards
          if (col < gridData[row].length - 1) {
            nextCol = col + 1;
          } else if (row < gridData.length - 1) {
            nextRow = row + 1;
            nextCol = 0;
          }
        }
        handled = true;
      }
      // Enter moves down (or saves on last cell)
      else if (e.key === 'Enter') {
        e.preventDefault();
        if (row === gridData.length - 1 && col === gridData[0].length - 1) {
          // Last cell - save
          if (onSave) onSave();
          handled = true;
        } else if (col < gridData[row].length - 1) {
          nextCol = col + 1;
          handled = true;
        } else if (row < gridData.length - 1) {
          nextRow = row + 1;
          nextCol = 0;
          handled = true;
        }
      }
      // Quick keys: 1, 0, - for observation values
      else if (e.key === '1' || e.key === '0' || e.key === '-') {
        onValueChange(row, col, e.key);
        // Move to next cell
        if (col < gridData[row].length - 1) {
          nextCol = col + 1;
        } else if (row < gridData.length - 1) {
          nextRow = row + 1;
          nextCol = 0;
        }
        handled = true;
      }

      if (handled) {
        e.preventDefault();
        setTimeout(() => {
          gridRef.current[nextRow]?.[nextCol]?.focus();
        }, 0);
      }
    },
    [gridData, onValueChange, onSave]
  );

  const setInputRef = useCallback((row: number, col: number, el: HTMLInputElement | null) => {
    if (!gridRef.current[row]) {
      gridRef.current[row] = [];
    }
    gridRef.current[row][col] = el;
  }, []);

  const focusCell = useCallback((row: number, col: number) => {
    setTimeout(() => {
      gridRef.current[row]?.[col]?.focus();
    }, 0);
  }, []);

  return { handleKeyDown, setInputRef, focusCell };
}
