declare module 'mammoth' {
  export function extractRawText(params: { arrayBuffer: ArrayBuffer }): Promise<{ value: string }>
}
