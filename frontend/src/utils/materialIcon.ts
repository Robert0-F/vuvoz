const CODE_ICONS: Record<string, string> = {
  paper: 'mdi-file-document-outline',
  cardboard: 'mdi-package-variant',
  canisters: 'mdi-bottle-tonic-outline',
  polyethylene: 'mdi-shrink',
  metal: 'mdi-cog',
  glass: 'mdi-glass-wine',
  plastic: 'mdi-bottle-soda-classic-outline',
}

export function materialMdiIcon(code: string, iconField?: string): string {
  if (iconField?.trim()) {
    const raw = iconField.trim()
    return raw.startsWith('mdi-') ? raw : `mdi-${raw}`
  }
  return CODE_ICONS[code] || 'mdi-recycle'
}
