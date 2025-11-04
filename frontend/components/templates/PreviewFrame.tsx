'use client';

interface PreviewFrameProps {
  device: 'desktop' | 'tablet' | 'mobile';
  children?: React.ReactNode;
  url?: string;
}

export default function PreviewFrame({ device, children, url }: PreviewFrameProps) {
  const deviceStyles = {
    desktop: 'w-full aspect-video',
    tablet: 'w-full max-w-2xl mx-auto aspect-[4/3]',
    mobile: 'w-full max-w-sm mx-auto aspect-[9/16]',
  };

  return (
    <div className="bg-white rounded-lg border border-neutral-200 p-8">
      <div className={`${deviceStyles[device]} bg-neutral-100 rounded-base flex items-center justify-center overflow-hidden`}>
        {url ? (
          <iframe src={url} className="w-full h-full border-0" title="Template Preview" />
        ) : children ? (
          children
        ) : (
          <p className="text-neutral-400">Template Preview</p>
        )}
      </div>
    </div>
  );
}

