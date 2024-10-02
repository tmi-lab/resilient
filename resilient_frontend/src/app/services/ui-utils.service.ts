import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UIUtilsService {
  private tailwindColors: string[] = [
    '--tw-color-red-500', '--tw-color-pink-500', '--tw-color-purple-500',
    '--tw-color-indigo-500', '--tw-color-blue-500', '--tw-color-green-500',
    '--tw-color-yellow-500', '--tw-color-orange-500', '--tw-color-teal-500',
    '--tw-color-cyan-500', '--tw-color-emerald-500', '--tw-color-lime-500',
    '--tw-color-amber-500', '--tw-color-rose-500', '--tw-color-violet-500',
    '--tw-color-fuchsia-500', '--tw-color-sky-500', '--tw-color-gray-500'
  ];

  constructor() { }

  getLineChartOptions(): any {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    return {
      maintainAspectRatio: false,
      aspectRatio: 0.6,
      plugins: {
          legend: {
              labels: {
                  color: textColor
              }
          }
      },
      scales: {
          x: {
              ticks: {
                  color: textColorSecondary
              },
              grid: {
                  color: surfaceBorder
              }
          },
          y: {
              ticks: {
                  color: textColorSecondary
              },
              grid: {
                  color: surfaceBorder
              }
          }
      }
  };
  }

  getRandomColor(): string {
    const randomIndex = Math.floor(Math.random() * this.tailwindColors.length);
    const colorVariable = this.tailwindColors[randomIndex];
    const documentStyle = getComputedStyle(document.documentElement);
    return documentStyle.getPropertyValue(colorVariable);
  }

  getColorWithTransparency(color: string, transparency: number): string {
    return this.hexToRgba(color, transparency);
  }


  private hexToRgba(hex: string, alpha: number): string {
    // Convert hex color to RGBA
    let r = 0, g = 0, b = 0;

    // 3 digits
    if (hex.length == 4) {
      r = parseInt(hex[1] + hex[1], 16);
      g = parseInt(hex[2] + hex[2], 16);
      b = parseInt(hex[3] + hex[3], 16);
    }
    // 6 digits
    else if (hex.length == 7) {
      r = parseInt(hex[1] + hex[2], 16);
      g = parseInt(hex[3] + hex[4], 16);
      b = parseInt(hex[5] + hex[6], 16);
    }

    return `rgba(${r}, ${g}, ${b}, ${alpha.toFixed(2)})`;
  }
}
