/**
 * Client-side digit masking utility.
 * Masks any sequence of 4 or more consecutive digits with XXXX
 * before the text is sent to the API.
 */

const DIGIT_PATTERN = /\d{4,}/g;

export interface MaskResult {
  masked: string;
  maskingOccurred: boolean;
}

export function maskDigits(input: string): MaskResult {
  let maskingOccurred = false;
  const masked = input.replace(DIGIT_PATTERN, (match) => {
    maskingOccurred = true;
    return "X".repeat(match.length);
  });
  return { masked, maskingOccurred };
}

