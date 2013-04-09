import fastkml.styles
import fastkml.config

# Monkeypatch to fix a bug making style maps use the normal style for highlight
def etree_element(self):
    element = super(fastkml.styles.StyleMap, self).etree_element()
    if self.normal:
        if isinstance(self.normal, (fastkml.styles.Style, fastkml.styles.StyleUrl)):
            pair = fastkml.config.etree.SubElement(element, "%sPair" %self.ns)
            key = fastkml.config.etree.SubElement(pair, "%skey" %self.ns)
            key.text = 'normal'
            pair.append(self.normal.etree_element())
    if self.highlight:
        if isinstance(self.highlight, (fastkml.styles.Style, fastkml.styles.StyleUrl)):
            pair = fastkml.config.etree.SubElement(element, "%sPair" %self.ns)
            key = fastkml.config.etree.SubElement(pair, "%skey" %self.ns)
            key.text = 'highlight'
            pair.append(self.highlight.etree_element()) # bug was here, said self.normal.etree_element()
    return element
fastkml.styles.StyleMap.etree_element = etree_element
