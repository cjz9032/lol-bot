import * as xx from 'win32-api';

export const GAME_WINDOW = 'League of Legends (TM) Client';
export const CLIENT_WINDOW = 'League of Legends';
const u32 = xx.User32.load(['FindWindowExW', 'GetWindowRect']);

const findByTitle = (title: string) => {
  return u32.FindWindowExW(0, 0, null, title);
};
export class WindowNotFound extends Error {
  constructor() {
    super('Window not found');
    this.name = 'WindowNotFound';
  }
}

export function checkWindowExists(windowName: string): boolean {
  const hwnd = findByTitle(windowName);
  if (!hwnd) {
    throw new WindowNotFound();
  }
  return true;
}

interface WindowRect {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export function getWindowSize(
  windowName: string
): [number, number, number, number] {
  const hwnd = findByTitle(windowName);
  if (!hwnd) {
    throw new WindowNotFound();
  }

  const rect = { left: 0, top: 0, right: 0, bottom: 0 } as WindowRect;
  const success = u32.GetWindowRect(hwnd, rect);
  if (!success) {
    throw new Error('Failed to get window rectangle');
  }

  return [rect.left, rect.top, rect.right, rect.bottom];
}

export function convertRatio(
  ratio: [number, number],
  windowName: string
): [number, number] {
  const [x, y, l, h] = getWindowSize(windowName);
  const updatedX = (l - x) * ratio[0] + x;
  const updatedY = (h - y) * ratio[1] + y;
  return [updatedX, updatedY];
}

getWindowSize(CLIENT_WINDOW);