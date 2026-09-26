import "react";

declare global {
  namespace React {
    namespace JSX {
      interface IntrinsicElements {
        "spline-viewer": React.DetailedHTMLProps<
          React.HTMLAttributes<HTMLElement> & {
            url?: string;
            "loading-anim-type"?: string;
          },
          HTMLElement
        >;
      }
    }
  }
  namespace JSX {
    interface IntrinsicElements {
      "spline-viewer": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          url?: string;
          "loading-anim-type"?: string;
        },
        HTMLElement
      >;
    }
  }
}
