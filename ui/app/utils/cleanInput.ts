export const trimLeadingZero = (num: string) => {
  if (num === ".") return "0.";
  const [integerPart] = num.split(".");
  if (integerPart.length > 1 && integerPart.startsWith("0"))
    return num.slice(1);
  return num;
};

export const removeCommas = (input: string) => {
  return input.replace(/,/g, "");
};
