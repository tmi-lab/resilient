import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'truncateDecimals'
})
export class TruncateDecimalPipe implements PipeTransform {
  transform(value: any, decimalPlaces: number = 2): any {
    if (this.isNumber(value) && this.hasDecimalPlaces(value)) {
      return parseFloat(value).toFixed(decimalPlaces);
    }
    return value;
  }

  private isNumber(value: any): boolean {
    return !isNaN(value) && value !== null && value !== '';
  }

  private hasDecimalPlaces(value: number): boolean {
    return value % 1 !== 0;
  }
}
